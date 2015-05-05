#-*- encoding: utf-8 -*-
import uuid,time,random,sys,datetime,traceback,os,json,math
from django.http import HttpResponse
from models import FixTask,RandomTask,RunningInfo
from utils import post

_task_timeout=85
_task_assign_num=5

class RunningStatus(object):
    
    def update(self):
        try:
            self.record=RunningInfo.objects.get(pk=self._id)
            self.fixtask_assign=eval(self.record.fixtask_assign)
            self.randomtask_assign=eval(self.record.randomtask_assign)
            self.next_assign_time=self.record.next_assign_time
            self.running_step=self.record.running_step
            self.heartbreak_sec=self.record.heartbreak_sec
        except:
            self.record.fixtask_assign='{}'
            self.record.randomtask_assign='{}'
            self.save()
            #print 'self.record.fixtask format error'
            self.fixtask_assign={}
            self.randomtask_assign={}
            
    def __init__(self):
        self._id=1
        try:
            self.record=RunningInfo.objects.get(pk=self._id)
            self.fixtask_assign=eval(self.record.fixtask_assign)
            self.randomtask_assign=eval(self.record.randomtask_assign)
            self.next_assign_time=self.record.next_assign_time
            self.running_step=self.record.running_step
            self.heartbreak_sec=self.record.heartbreak_sec
        except:
            self.record.fixtask_assign='{}'
            self.record.randomtask_assign='{}'
            self.save()
            #print 'self.record.fixtask format error'
            self.fixtask_assign={}
            self.randomtask_assign={} 
        
    def save(self):
        self.record.fixtask_assign=self.fixtask_assign.__repr__()
        self.record.randomtask_assign=self.randomtask_assign.__repr__()
        self.record.next_assign_time=self.next_assign_time
        self.record.running_step=self.running_step
        self.record.heartbreak_sec=self.heartbreak_sec
        self.record.save()
        
    def assign_fixtask(self):
        atl={}
        fixtask_list = FixTask.objects.filter(enable=True).order_by('id')
        for t in fixtask_list:
            if datetime.datetime.now()-t.last_submit_time>datetime.timedelta(seconds=get_interval(t.interval)):#get_interval(t.interval)
                t.assign_times+=1
                t.last_submit_time=datetime.datetime.now()
                t.save()
                d={'assgin_time':0,'status':'waiting','retry_times':0}
                atl[t.id]=d
        self.fixtask_assign=atl
        RunningInfo.objects.filter(id=1).update(fixtask_assign=self.fixtask_assign.__repr__())
    def pop_fixtask(self,count):
        r=[]
        self.update()
        for k,t in self.fixtask_assign.items():
            if t['retry_times']>2:
                #报警
                self.fixtask_assign.pop(k)
                continue
            if time.time()-t['assgin_time']>_task_timeout:
                r.append(k)
                t['status']='running'
                t['assgin_time']=time.time()
                t['retry_times']+=1
                if len(r)<count:
                    continue
                else:
                    break
        self.save()
        tasks=[]
        for i in r:
            d={}
            ft=FixTask.objects.get(pk=i)
            if not ft ==None:
                business_id=0 if ft.business_id==None else ft.business_id
                parser_id=0 if ft.parser_id==None else ft.parser_id
                next_parser_id=0 if ft.next_parser_id==None else ft.next_parser_id
                if ft.url==None or ft.url=='':
                    #print 'Fixtask[%d] url is null'%ft.id
                    continue
                param='{}' if ft.param=='' or ft.param==None else ft.param
                ft.assign_times+=1
                
                d['parser_id']=ft.parser_id
                d['param']="'FixTask',%d,%d,%d,'%s',%d,**%s"%(ft.id,business_id,next_parser_id,ft.url,ft.assign_times,param)
                ft.last_assign_time=datetime.datetime.now()
                ft.save()
                tasks.append(d)
            else:
                #print 'no randomtask id =%d'%i
                pass
        return tasks
    def remove_fixtask(self,id):
        self.update()
        self.fixtask_assign.pop(id)
        self.save()
    def get_fixtask(self,id):
        return self.fixtask_assign[id]
    def get_fixtask_count(self):
        return len(self.fixtask_assign)
    
    
    def pop_task(self):
        tasks=self.pop_fixtask(_task_assign_num)
        if len(tasks)<_task_assign_num:
            tasks+=self.pop_randomtask(_task_assign_num-len(tasks))
        if len(tasks)<_task_assign_num:
            self.set_running_step(1)
        return random.sample(tasks, len(tasks))
    
    def clear_task(self):
        self.fixtask_assign.clear()
        self.randomtask_assign.clear()
        self.save()
    def timeout_task(self):
        self.update()
        for k,v in self.fixtask_assign.items():
            if time.time()-v['assgin_time']>_task_timeout:
                if v['retry_times']>2:
                    self.fixtask_assign.pop(k)
                    ft=FixTask.objects.get(pk=k)
                    ft.assign_times+=1
                    ft.save()
                else:
                    v['status']='waiting'
                    v['assgin_time']=0
                    v['retry_times']+=1
        self.save()
        for k,v in self.randomtask_assign.items():
            if time.time()-v['assgin_time']>_task_timeout:
                if v['retry_times']>2:
                    self.randomtask_assign.pop(k)
                    rt=RandomTask.objects.get(pk=k)
                    rt.state=-1
                    rt.note='timeout'
                    rt.save()
                else:
                    v['status']='waiting'
                    v['assgin_time']=0
                    v['retry_times']+=1
        self.save()
        
    def add_randomtask(self,id,fixid):
        d={'fixtask_id':fixid,'assgin_time':0,'status':'waiting','retry_times':0}
        self.update()
        self.randomtask_assign[id]=d
        self.save()
    def remove_randomtask(self,id):
        self.update()
        self.randomtask_assign.pop(id)
        self.save()
    def pop_randomtask(self,count):
        r=[]
        self.update()
        for k,t in self.randomtask_assign.items():
            if t['retry_times']>2:
                #报警
                self.randomtask_assign.pop(k)
                continue
            if time.time()-t['assgin_time']>_task_timeout:
                r.append(k)
                t['status']='running'
                t['assgin_time']=time.time()
                t['retry_times']+=1
                if len(r)<count:
                    continue
                else:
                    break
        self.save()
        tasks=[]
        for i in r:
            d={}
            rt=RandomTask.objects.get(pk=i)
            if not rt==None:
                business_id=0 if rt.business_id==None else rt.business_id
                parser_id=0 if rt.parser_id==None else rt.parser_id
                next_parser_id=0 if rt.next_parser_id==None else rt.next_parser_id
                if rt.url==None or rt.url=='':
                    #print 'Randomtask[%d] url is null'%rt.id
                    continue
                param='{}' if rt.param=='' or rt.param==None else rt.param
                #print rt.business_id,rt.parser_id,rt.next_parser_id,rt.url,rt.param
                rt.error_count+=1
                d['parser_id']=rt.parser_id
                d['param']="'RandomTask',%d,%d,%d,'%s',%d,**%s"%(i,business_id,next_parser_id,rt.url,rt.error_count,param)
                rt.last_assign_time=datetime.datetime.now()
                rt.save()
                tasks.append(d)
            else:
                #print 'no randomtask id =%d'%i
                pass
        return tasks
    def get_randomtask(self,id):
        self.update()
        return self.randomtask_assign[id]
    def get_randomtask_count(self):
        self.update()
        return len(self.randomtask_assign)
        
    def get_next_assign_time(self):
        self.update()
        return self.next_assign_time
    def gen_next_assign_time(self):
        self.next_assign_time=datetime.datetime.now()+datetime.timedelta(seconds=self.heartbreak_sec)
        self.running_step=0
        RunningInfo.objects.filter(id=1).update(next_assign_time=self.next_assign_time,running_step=0)
    def is_next_assign_time(self):
        self.update()
        if time.time()-time.mktime(self.next_assign_time.timetuple())>0:
            return True
        else:
            return False
        
    def get_sleep_sec(self):
        delta=int(time.mktime(self.next_assign_time.timetuple())-time.time())
        if delta>0:
            return delta+random.randint(1,5)
        else:
            #still running but no new task
            return 30
    
    #sleeping无任务
    #assigning有未分配任务
    #running所有任务均分配完毕，但有未返回执行结果的任务
    def get_task_state(self):
        self.update()
        if self.get_fixtask_count()==0 and self.get_randomtask_count()==0:
            return 'notask'
        for ft in self.fixtask_assign.values():
            if ft['status']=='waiting':
                return 'assigning'
        #fixtask分配完了
        for rt in self.randomtask_assign.values():
            if rt['status']=='waiting':
                return 'assigning'
        return 'running'
    
    def show_task_state(self):
        output='next_time=%s</br>next_sec=%d</br>running_step=%d</br></br>fixtask_assign=%d</br>%s</br></br>randomtask_assign=%d</br>%s</br></br>'\
        %(self.next_assign_time,int(time.mktime(self.next_assign_time.timetuple())-time.time()),self.running_step,\
          len(self.fixtask_assign),self.fixtask_assign.__repr__(),len(self.randomtask_assign),self.randomtask_assign.__repr__())
        return output
    
    #0 sleeping
    #1分配fixtask
    #2 fixtask分配完但未执行完，random为空
    #3 fixtask分配完但未执行完，random不空
    #4 fixtask执行完已空，random未空
    def get_running_step(self):
        return self.running_step
    def set_running_step(self,b):
        RunningInfo.objects.filter(id=1).update(running_step=b)
        self.running_step=b
        
def get_task_list():
    runinfo=RunningStatus()
    try:
        flag=runinfo.get_task_state()
        #print 'now()-next_assign_time = %d flag=%s runsetp=%d'%(runinfo.get_sleep_sec(),flag,runinfo.running_step)
        if runinfo.is_next_assign_time() and flag=='notask':#执行时间到了and没有任务=查询任务并pop
            #print '111111111111111111111111111'
            if runinfo.get_running_step()>0:
                runinfo.gen_next_assign_time()
                runinfo.set_running_step(0)
                sleep_seconds={'sleep_seconds':runinfo.get_sleep_sec()}
                return sleep_seconds
            else:
                #print '2222222222222222222222'
                runinfo.set_running_step(1)
                runinfo.assign_fixtask()
                return runinfo.pop_task()
        elif not runinfo.is_next_assign_time() and flag=='notask':
            #print '3333333333333333'
            runinfo.set_running_step(0)
            sleep_seconds={'sleep_seconds':runinfo.get_sleep_sec()}
            return sleep_seconds
        elif runinfo.is_next_assign_time() and flag=='assigning':#执行时间到了and有任务=pop任务出来
                return runinfo.pop_task()
        elif runinfo.is_next_assign_time() and flag=='running':#执行时间到了and所有任务已分配但未执行完=sleep
            run_passed_time=(-int(time.mktime(runinfo.next_assign_time.timetuple())-time.time()))
            if run_passed_time>_task_timeout:#最后分配出去的任务timeout
                #直接清除是否合适？
                runinfo.timeout_task()
                runinfo.gen_next_assign_time()
                runinfo.set_running_step(0)
                sleep_seconds={'sleep_seconds':runinfo.get_sleep_sec()}
                return sleep_seconds
            else:#running
                #print 'flag==running next_assign_time = %ds later'%(-runinfo.get_sleep_sec())
                sleep_seconds={'sleep_seconds':runinfo.get_sleep_sec()}#30
                return sleep_seconds
        sleep_seconds={'sleep_seconds':runinfo.get_sleep_sec()}
        return sleep_seconds
    except Exception,e:
        info = sys.exc_info()
        #print "* %s: %s" % info[:2]
        #for file, lineno, function, text in traceback.extract_tb(info[2]):
            #print "*error@%s , line %s , in %s()"%(os.path.split(file)[1],lineno,function)
        return {'sleep_seconds':runinfo.get_sleep_sec(),'error':flag+str(e)}

def submit_fixtask(data):
    runinfo=RunningStatus()
    if data['task_info']['success']:
        error=''
        ftid=data['task_info']['task_id']
        try:
            ft= FixTask.objects.get(pk=ftid)
            if ft.assign_times!=data['task_info']['assign_token']:
                #过时的token，可能是timeout的任务submit
                runinfo.remove_fixtask(ftid)
                return HttpResponse('token=%d timeout'%data['task_info']['assign_token'])
            self_param=json.dumps(data['task_info']['self_param'])
            ft.param=self_param
            ft.error_count=0
            ft.submit_times+=1
            ft.message_count+=len(data['message'])
            ft.last_submit_time=datetime.datetime.now()
            ft.save()
            runinfo.remove_fixtask(ftid)
        except Exception,e:
            errorstr='Add FixTask Result Error='+str(e)
            error+='['+errorstr+']'
            #info = sys.exc_info()
            #print "* %s: %s" % info[:2]
            #for file, lineno, function, text in traceback.extract_tb(info[2]):
                #print "*error@%s , line %s , in %s()"%(os.path.split(file)[1],lineno,function)
        
        for m in data['message']:
            try:
                rt=RandomTask(business_id=data['task_info']['business_id'],
                              fixtask_id=data['task_info']['task_id'],
                              parser_id=None if data['task_info']['next_parser_id']==0 else data['task_info']['next_parser_id'],
                              pre_parser_id=data['task_info']['cur_parser_id'],
                              url=m['data']['Url'],
                              state=m['state'],
                              pre_result=json.dumps(m['data'], ensure_ascii=False),
                              last_submit_time=datetime.datetime.now())
                rt.save()
                if m['state']==1:
                    #print rt.url
                    post_message(rt.pre_result)
                else:
                    runinfo.add_randomtask(rt.id,ftid)
                    runinfo.set_running_step(3)
                    #print 'add randomtask id =%s'%rt.id
            except Exception,e:
                errorstr='Add FixTask_RandomTask Result Error='+str(e)
                #print 'ERROR URL=',m['data']['Url']
                error+='['+errorstr+']'
                #info = sys.exc_info()
                #print "* %s: %s" % info[:2]
                #for file, lineno, function, text in traceback.extract_tb(info[2]):
                    #print "*error@%s , line %s , in %s()"%(os.path.split(file)[1],lineno,function)
                continue
        echo='success' if error=='' else error
        #runinfo.save()
        return HttpResponse(echo)
    else:
        #处理错误信息
        runtask=runinfo.get_fixtask(data['task_info']['task_id'])
        if runtask['retry_times']>2:
            #如果重试3次了,报警
            ft=FixTask.objects.get(id=data['task_info']['task_id'])
            ft.error_count+=1
            ft.note=time.strftime('%Y-%m-%d %H:%M:%S')+'='+data['task_info']['error']
            ft.save()
            #print 'fixtask %d failed 3 times,pop it'%ftid
            runinfo.remove_fixtask(data['task_info']['task_id'])
        return HttpResponse('parse failed '+data['task_info']['error'])

def submit_randomtask(data):
    runinfo=RunningStatus()
    if data['task_info']['success']:
        error=''
        for m in data['message']:
            #print m['data']
            try:
                #!!m['id]==0? 0新增
                rt=RandomTask.objects.get(pk=m['id'])
                if rt.state==1:
                    runinfo.remove_randomtask(rt.id)
                    return HttpResponse('Random[%d] already submitted'%rt.id)
                if rt.error_count!=data['task_info']['assign_token']:
                    #过时的token，可能是timeout的任务submit
                    runinfo.remove_randomtask(rt.id)
                    runinfo.save()
                    return HttpResponse('token=%d timeout'%data['task_info']['assign_token'])
                pre_result=json.loads(rt.pre_result)
                keys=m['data'].keys()
                for k in keys:
                    if m['data'][k]=='' and pre_result.has_key(k):
                        m['data'][k]=pre_result[k]
                #!!fixtask_id=t.fixtask_id,?
                rt.pre_result=json.dumps(m['data'], ensure_ascii=False)
                rt.pre_parser_id=None if data['task_info']['cur_parser_id']==0 else data['task_info']['cur_parser_id']
                rt.next_parser_id=None if data['task_info']['next_parser_id']==0 else data['task_info']['next_parser_id']
                rt.state=m['state']
                self_param=json.dumps(data['task_info']['self_param']) if data['task_info'].has_key('self_param') else ''
                rt.param=self_param
                rt.last_submit_time=datetime.datetime.now()
                rt.save()
                    
                if m['state']==1:
                    runinfo.remove_randomtask(rt.id)
                    #print rt.url
                    post_message(rt.pre_result)
                else:
                    r=get_randomtask(data['task_info']['task_id'])
                    r['assgin_time']=0
                    r['status']='waiting'
                    r['retry_times']=0
                    runinfo.set_running_step(2)
                    #print 'continue assign randomtask id =%s'%rt.id
            except Exception,e:
                if runinfo.randomtask_assign[m['id']].retry_times>2:
                    #如果重试3次了,报警
                    #print 'fixtask %d failed 3 times,pop it'%m['id']
                    runinfo.remove_randomtask(m['id'])
                else:
                    runinfo.get_randomtask[data['task_info']['task_id']]['assgin_time']=0
                    runinfo.get_randomtask[data['task_info']['task_id']]['status']='waiting'
                    runinfo.get_randomtask[data['task_info']['task_id']]['retry_times']+=1
                errorstr='Update RandomTask Error='+str(e)
                error+='['+errorstr+']'
                #print error
                continue
        echo='success' if error=='' else error
        return HttpResponse(echo)
    else:
        if runinfo.get_randomtask[data['task_info']['task_id']]['retry_times']>2:
            #如果重试3次了,报警
            rt=RandomTask.objects.get(id=data['task_info']['task_id'])
            rt.note=time.strftime('%Y-%m-%d %H:%M:%S')+'='+data['task_info']['error']
            rt.save()
            #print 'fixtask %d failed 3 times,pop it'%ftid
            runinfo.remove_randomtask(data['task_info']['task_id'])
        else:
            runinfo.get_randomtask[data['task_info']['task_id']]['assgin_time']=0
            runinfo.get_randomtask[data['task_info']['task_id']]['status']='waiting'
            runinfo.get_randomtask[data['task_info']['task_id']]['retry_times']+=1
            runinfo.save()
        return HttpResponse(data['task_info']['error'])


#向前台服务器post信息
def post_message(message):
    post_url='http://floating-autumn-9293.heroku.com/photograph_messages/create_by_json'
    try:
        json_str=None
        if type(message) is unicode:
            json_str=message
        elif type(message) is dict:
            for k in message.keys():
                if type(message[k]) is unicode:
                    message[k]=message[k].encode('utf-8',errors='ignore')
            json_str=json.dumps(message, ensure_ascii=False)
            #print message['Url']
        
        data={'json_str':json_str.encode('utf-8',errors='ignore')}
        #print data
        #echo=post(post_url, data)
        #print 'post_message success!'
        #print message
        return True
    except Exception,e:
        #print 'post_message error=%s'%(str(e))
        #print message
        return False

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