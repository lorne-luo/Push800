#-*- encoding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.db.models import F
from models import *
from spiderserver.frontserver.message_views import add_message

import datetime,json,random,sys,traceback,os,time
import spider_manager as sm
from spiderserver.utils.mail import send_mutil_email,send_single_email

'''发布任务的间隔'''
INTERVAL=15
_task_assign_num=5
_task_timeout=150
_heartbreak_interval=210
_random_interval=6

def test(request):
    now=datetime.datetime.now()
    html='it is %s'%now
    #return HttpResponse(str(request.META))
    global INTERVAL
    return HttpResponse(str(INTERVAL))

def object_list(request, model):
    obj_list = model.objects.all()
    template_name = '%s_list.html' % model.__name__.lower()
    return render_to_response(template_name, {'object_list': obj_list})

'''发布任务'''
#http://192.168.109.123:8000/spiderserver/gettasks/
def gettasks(request):
    #更新spider最后请求时间
    spiderinfo=json.loads(request.POST['spiderinfo'])
    sm.update_live_spider(spiderinfo['token'])
    sm.update_last_run()

    global _task_timeout,_random_interval

    if time.time()<sm.get_next_assign_time():
        #每隔_random_interval分开节点访问服务器的时间，避免脏读
        interval=sm.get_assign_gap()+_random_interval*sm.get_spider_count()
        sm.inc_spider_count()
        sleep_seconds={'sleep_seconds':interval}
        return HttpResponse(json.dumps(sleep_seconds, ensure_ascii=False))

    tasks=[]
    fixtask_list = FixTask.objects.filter(enable=True,\
                    last_assign_time__lt=datetime.datetime.now()-datetime.timedelta(seconds=_task_timeout)).order_by('-id')
    #fixtask_list = FixTask.objects.all().order_by('-id')
    for t in fixtask_list:
        if datetime.datetime.now()-t.last_submit_time>datetime.timedelta(seconds=get_interval(t.interval)):
            t.assign_times+=1
            t.last_assign_time=datetime.datetime.now()
            t.save()
            p={}
            parser_id=t.parser_id if t.parser_id!=None else 0
            next_parser_id=t.next_parser_id if t.next_parser_id!=None else 0
            self_param={} if t.param=='' or t.param==None else json.loads(t.param)
            
            p['parser_id']=parser_id
            p['param']="'FixTask',%d,%d,%d,'%s',%d,**%s"%(t.id,t.business_id,next_parser_id,t.url,t.assign_times,self_param)
            tasks.append(p)
        if len(tasks)==_task_assign_num:
            break

    if len(tasks):
        sm.set_running_step(0)
    if len(tasks)<_task_assign_num:
        limit=_task_assign_num-len(tasks)
        randomtask_list = RandomTask.objects.filter(last_assign_time__lt=datetime.datetime.now()-datetime.timedelta(seconds=_task_timeout),\
                                state=0)[0:limit]
        for t in randomtask_list:
            t.last_assign_time=datetime.datetime.now()
            t.assign_times+=1
            t.save()
            
            p={}
            parser_id=t.parser_id if t.parser_id!=None else 0
            next_parser_id=t.next_parser_id if t.next_parser_id!=None else 0
            self_param={} if t.param=='' or t.param==None else json.loads(t.param)
            
            p['parser_id']=parser_id
            p['param']="'RandomTask',%d,%d,%d,'%s',%d,**%s"%(t.id,t.business_id,next_parser_id,t.url,t.assign_times,self_param)
            tasks.append(p)
            
    if len(tasks)==0:
        #两种情况
        sleep_seconds={}
        if sm.get_running_step()>0:
            #本轮任务分配全部执行完毕，有新消息
            interval=get_heartbreak_sec()
            sm.set_next_assign_time(time.time()+interval)
            sm.set_running_step(0)
            sm.set_spider_count(1)
            sleep_seconds={'sleep_seconds':interval}
        elif sm.get_running_step()==0:#fixtask分配完毕但还未提交
            fixtask_list=FixTask.objects.filter(enable=True,last_assign_time__gt=F('last_submit_time'))
            #正在运行的fixtask个数>0
            if len(fixtask_list):
                #半sleep
                sleep_seconds={'sleep_seconds':30+random.randint(1,_random_interval)}
            else:
                #本轮任务分配全部执行完毕，无新消息
                interval=get_heartbreak_sec()
                sm.set_next_assign_time(time.time()+interval)
                sm.set_running_step(0)
                sm.set_spider_count(1)
                sleep_seconds={'sleep_seconds':interval}

        return HttpResponse(json.dumps(sleep_seconds, ensure_ascii=False))
    else:
        return HttpResponse(json.dumps(tasks, ensure_ascii=False))


def get_fix_task(request):
    #更新spider最后请求时间
    
    return HttpResponse(json.dumps(assign_fixtask(), ensure_ascii=False))

def assign_fix_task(request):
    return HttpResponse(json.dumps(assign_fixtask(), ensure_ascii=False))
    
'''提交任务'''
def submittask(request):
    try:
        data=json.loads(request.POST['result'])
        #更新spider最后请求时间
        #sm.update_live_spider(spiderinfo['token'])
        sm.update_last_submit()
        
        if data['task_info']['task_type']=='FixTask':
            return submitfixtask(data)
        elif data['task_info']['task_type']=='RandomTask':
            return submitrandomtask(data)
        return HttpResponse('success')
    except Exception,e:
        return HttpResponse('['+str(e)+']')

'''提交Fix任务'''
def submitfixtask(data):
    if data['task_info']['success']:
        ftid=data['task_info']['task_id']
        ft= FixTask.objects.get(pk=ftid)
        if ft.assign_times!=data['task_info']['assign_token']:
            return HttpResponse('token[%d] timeout'%data['task_info']['assign_token'])
        else:
            ft.error_count=0
            ft.last_submit_time=datetime.datetime.now()
            ft.param=json.dumps(data['task_info']['self_param'])
            ft.submit_times+=1
            ft.message_count+=len(data['message'])
            #ft.note=''
            ft.save()
        error=''
        for m in data['message']:
            try:
                rt=RandomTask(business_id=data['task_info']['business_id'],
                              fixtask_id=data['task_info']['task_id'],
                              parser_id=None if data['task_info']['next_parser_id']==0 else data['task_info']['next_parser_id'],
                              pre_parser_id=data['task_info']['cur_parser_id'],
                              url=m['data']['Url'],
                              state=m['state'],
                              pre_result=json.dumps(m['data'], ensure_ascii=False),
                              last_submit_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                if rt.state==1:#一次爬行就是终态了
                    #print rt.url
                    parser=SpiderParser.objects.get(pk=data['task_info']['cur_parser_id'])
                    m['data']['Site_id']=parser.site_id
                    b,s=add_message(data['task_info']['business_id'],m['data'],rt.id)
                    if b:
                        rt.state=2
                    else:
                        rt.note=s
                else:
                    sm.set_running_step(2)
                rt.save()
            except Exception,e:
                error=str(e)
                info = sys.exc_info()
                #print "* %s: %s" % info[:2]
                for file, lineno, function, text in traceback.extract_tb(info[2]):
                    error+= "|%s , line %s , in %s()"%(os.path.split(file)[1],lineno,function)
                continue
        echo='success' if error=='' else error
        return HttpResponse(echo)
    else:
        #处理错误信息
        ft=FixTask.objects.get(id=data['task_info']['task_id'])
        if ft.error_count>9:
            #TODO 连续异常10次向开发者报警
            try:
                send_single_email('leandro@qq.com',u'SpiderServer Fault',ft.parser.class_name+u' 连续十次错误<br/>'+data['task_info']['error'].__repr__())
            except :
                pass
            ft.error_count=0
        else:
            ft.error_count+=1
            ft.note='error_count='+str(ft.error_count)+' '+data['task_info']['error'].__repr__()
        ft.save()
        return HttpResponse('failed:%s error_count=%d'%(data['task_info']['error'].__repr__(),ft.error_count))
        
'''提交Random任务'''
def submitrandomtask(data):
    sm.set_running_step(3)
    if data['task_info']['success']:
        error='success'
        for m in data['message']:
            #print m['data']
            if type(m['id']) is int and m['id']>0:#更新
                try:
                    rt=RandomTask.objects.get(pk=m['id'])
                    #如果rt没取到怎么办？
                    if rt==None:
                        #print 'No RandomTask id=%d',m['id']
                        continue
                    #过时的token，可能是timeout的任务submit
                    if rt.assign_times!=data['task_info']['assign_token']:
                        return HttpResponse('token[%d] timeout'%data['task_info']['assign_token'])
                    
                    #合并前次结果
                    pre_result=json.loads(rt.pre_result)
                    keys=m['data'].keys()
                    for k in keys:
                        if (m['data'][k]=='' or m['data'][k]==0 or m['data'][k]==[]) and pre_result.has_key(k):
                            m['data'][k]=pre_result[k]

                    rt.pre_result=json.dumps(m['data'], ensure_ascii=False)
                    #rt.pre_parser_id=None if data['task_info']['cur_parser_id']==0 else data['task_info']['cur_parser_id']
                    #rt.next_parser_id=None if data['task_info']['next_parser_id']==0 else data['task_info']['next_parser_id']
                    rt.state=m['state']
                    
                    self_param=json.dumps(data['task_info']['self_param']) if data['task_info'].has_key('self_param') else '{}'
                    rt.param=self_param
                    rt.last_submit_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    #print rt.url
                    if m['state']:
                        parser=SpiderParser.objects.get(pk=data['task_info']['cur_parser_id'])
                        m['data']['Site_id']=parser.site_id
                        b,s=add_message(data['task_info']['business_id'],m['data'],rt.id)
                        if b:
                            rt.state=2
                        else:
                            rt.note=s
                    rt.save()
                except Exception,e:
                    error=str(e)
                    info = sys.exc_info()
                    #print "* %s: %s" % info[:2]
                    for file, lineno, function, text in traceback.extract_tb(info[2]):
                        error+= "|%s , line %s , in %s()"%(os.path.split(file)[1],lineno,function)
                    continue
            else:#新增
                try:
                    #print m['data']
                    rt=RandomTask(business_id=data['task_info']['business_id'],
                              parser_id=data['task_info']['next_parser_id'],
                              pre_parser_id=data['task_info']['cur_parser_id'],
                              url=m['data']['Url'],
                              state=m['state'],
                              pre_result=json.dumps(m['data'], ensure_ascii=False),
                              last_submit_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    if m['state']:
                        parser=SpiderParser.objects.get(pk=data['task_info']['cur_parser_id'])
                        m['data']['Site_id']=parser.site_id
                        b,s=add_message(data['task_info']['business_id'],m['data'],rt.id)
                        if b:
                            rt.state=2
                        else:
                            rt.note=s
                    rt.save()
                    error=str(rt.id)
                except Exception,e:
                    error=str(e)
                    info = sys.exc_info()
                    #print "* %s: %s" % info[:2]
                    for file, lineno, function, text in traceback.extract_tb(info[2]):
                        error+= "|%s , line %s , in %s()"%(os.path.split(file)[1],lineno,function)
                    continue
        echo=error
        return HttpResponse(echo)
    else:
        #处理错误信息
        rt=RandomTask.objects.get(id=data['task_info']['task_id'])
        if rt.error_count>2:
            #连续异常3次向开发者报警
            rt.state=-1
        else:
            rt.note=data['task_info']['error'].__repr__()
            rt.error_count+=1
        rt.save()
        return HttpResponse('failed:%s , error_count=%d'%(data['task_info']['error'].__repr__(),rt.error_count))
    
def get_interval(i):
    h=int(time.strftime('%H'))
    if h<3:
        return int(i*1.8)
    elif h<8:
        return random.randint(2000,3600)
    elif h<9:
        return int(i*1.5)
    elif h<12:
        return i
    elif h<15:
        return int(i*1.3)
    elif h<18:
        return int(i*1.1)
    elif h<20:
        return int(i*1.4)
    elif h<24:
        return int(i*1.2)
    return int(i*1.5)
    
def get_heartbreak_sec():
    h=int(time.strftime('%H'))
    if h<3:
        return int(_heartbreak_interval*2)
    elif h<8:
        return random.randint(2000,3600)
    elif h<9:
        return int(_heartbreak_interval*2)
    elif h<12:
        return _heartbreak_interval
    elif h<15:
        return int(_heartbreak_interval*1.3)
    elif h<18:
        return int(_heartbreak_interval*1.1)
    elif h<20:
        return int(_heartbreak_interval*1.8)
    elif h<24:
        return int(_heartbreak_interval*1.4)
    return int(_heartbreak_interval*2)
    
    
    
#------------------------------------MODULES--------------------------------------------------

def update_fixtask(request):
    #只会更新必要字段
    #Publisher.objects.filter(id=52).update(name='Apress Publishing')
    pass
    
def get_modules(request):
    return HttpResponse(json.dumps(get_modules_info(), ensure_ascii=False))

def get_modules_info():
    res=[]
    modules = SpiderParser.objects.all().order_by('id')
    for m in modules:
        item={'parser_id':m.id,'module_name':m.module_name,'class_name':m.class_name,'version':m.version,}
        res.append(item)
    return res

def update_modules(request):
    data=json.loads(request.POST['modules'])
    return HttpResponse(request.POST['modules'])

#------------------------------------SPIDERS--------------------------------------------------

def spider_login(request):
    resp={}
    try:
        data=json.loads(request.POST['login_data'])
        ip=''
        if request.META.has_key('HTTP_X_FORWARDED_FOR'):
            ip =  request.META['HTTP_X_FORWARDED_FOR']
        elif request.META.has_key('REMOTE_ADDR'):
            ip =  request.META['REMOTE_ADDR']
        
        #mac=uuid.UUID(int=data['macint'])
        #token=str(uuid.uuid5(mac,ip))
        token=str(data['macint'])
        
        sm.add_spider(token,ip,data['machine_name'])
        mods=get_modules_info()
        
        
        resp['token']=token
        resp['success']=True
        resp['modules']=mods
    except Exception,e:
        resp['token']=None
        resp['success']=False
        resp['error']=str(e)
    return HttpResponse(json.dumps(resp, ensure_ascii=False))

def get_spiders(request):
    spiders=sm.get_spiders_info()
    html=str(len(spiders))+'</br>'
    for k,v in spiders.items():
        #html+=v['login_time'].strftime('%Y-%m-%d %H:%M:%S')
        html+='%s</br>%s</br>%s</br>%s</br>%s</br></br>'%(k,v['ip'],v['spider_name'],\
            v['last_login_time'].strftime('%Y-%m-%d %H:%M:%S'),v['last_request_time'].strftime('%Y-%m-%d %H:%M:%S'))
    return HttpResponse(html)


        
def send_zipfile(request):  
    """                                                                          
    Create a ZIP file on disk and transmit it in chunks of 8KB,                  
    without loading the whole file into memory. A similar approach can           
    be used for large dynamic PDF files.                                         
    """  
    temp = tempfile.TemporaryFile()  
    archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)  
    for index in range(10):  
        filename = __file__ # Select your files here.                              
        archive.write(filename, 'file%d.txt' % index)  
    archive.close()  
    wrapper = FileWrapper(temp)  
    response = HttpResponse(wrapper, content_type='application/zip')  
    response['Content-Disposition'] = 'attachment; filename=test.zip'  
    response['Content-Length'] = temp.tell()  
    temp.seek(0)
    return response  

def running_status(request):
    output='''服务器时间 = %s</br>
        下次调度任务时刻 = %s</br>
        距离下次调度任务时刻  = %d s</br>
        爬虫节点数 = %d</br>
        运行阶段 = %d</br></br>
        最新一条消息提交时间 = %s</br>
        最后爬虫节点执行任务时间 = %s</br>'''\
        %(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),\
          datetime.datetime.fromtimestamp(sm.get_next_assign_time()).strftime('%Y-%m-%d %H:%M:%S'),\
          sm.get_assign_gap(),sm.get_spider_count(),sm.get_running_step(),sm.get_last_submit(),sm.get_last_run())
    return HttpResponse(output)

def last_run_time(request):
    nodelist=SpiderNode.objects.all().order_by('-last_assign_time')[:1]
    node=nodelist[0]
    res=str(int(time.mktime(node.last_assign_time.timetuple())))
    return HttpResponse(res)