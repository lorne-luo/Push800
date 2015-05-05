#-*- encoding: utf-8 -*-
from django.contrib import admin
from django.http import HttpResponse
from models import *
from spider_manager import *
import uuid,time,random,sys
from utils import post
    
_fixtask={}
_randomtask={}
_randomtask_id=0
_task_token=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#每个spider每次分配的任务数
_task_assign_num=5
_next_assign_time=time.time()
_assign_interval=119
_is_running=False

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

def assign_fixtask():
    fixtask_list = FixTask.objects.filter(enable=True).order_by('id')
    global _fixtask
    for t in fixtask_list:
        if datetime.datetime.now()-t.last_submit_time>datetime.timedelta(seconds=get_interval(t.interval)):#t.interval
            mft=Mem_FixTask(t)
            t.assign_times+=1
            t.save()
            _fixtask[mft.id]=mft
#sleeping无任务
#assigning有未分配任务
#running所有任务均分配完毕，但有未返回执行结果的任务
def get_task_state():
    if len(_fixtask)==0 and len(_randomtask)==0:
        return 'notask'
    for t in _fixtask.values():
        if not t.is_assigned():
            return 'assigning'
    #fixtask分配完了
    for v in _randomtask.values():
        if not v.is_assigned():
            return 'assigning'
    return 'running'

def get_task_info():
    #时间到了and没有任务=查询任务出来
    try:
        global _next_assign_time,_fixtask,_randomtask,_assign_interval,_is_running
        
        flag=get_task_state()
        
        if time.time()>_next_assign_time and flag=='notask':#执行时间到了and没有任务=查询任务并pop
            if _is_running:
                _next_assign_time=time.time()+_assign_interval
                _is_running=False
                sleep_seconds={'sleep_seconds':int(_next_assign_time-time.time()+1)}
                return sleep_seconds
            else:
                _is_running=True
                assign_fixtask()
                return pop_task()
        elif time.time()<_next_assign_time and flag=='notask':
            _is_running=False
            sleep_seconds={'sleep_seconds':int(_next_assign_time-time.time()+1)}
            return sleep_seconds
        elif time.time()>_next_assign_time and flag=='assigning':#执行时间到了and有任务=pop任务出来
                return pop_task()
        elif time.time()>_next_assign_time and flag=='running':#执行时间到了and所有任务已分配但未执行完=sleep
            if time.time()-_next_assign_time>_assign_interval/2:#最后分配出去的任务timeout
                clear_task()
                _next_assign_time=time.time()+_assign_interval
                sleep_seconds={'sleep_seconds':int(_next_assign_time-time.time()+1)}
                return sleep_seconds
            else:#running
                print 'flag==running next_assign_time = %.0f s later'%(_next_assign_time-time.time())
                sleep_seconds={'sleep_seconds':30}
                return sleep_seconds
        print 'flag=%s next_assign_time = %.0f s later'%(flag,_next_assign_time-time.time())
        sleep_seconds={'sleep_seconds':int(_next_assign_time-time.time()+1)}
        return sleep_seconds
    except Exception,e:
        print 'get_task_info err=',str(e)
        
    
    
def pop_task():
    global _next_assign_time,_fixtask,_randomtask,_assign_interval
    tasks=[]
    for i in range(_task_assign_num):
        p=None
        for k,v in _fixtask.items():
            if not v.is_assigned():
                p=v.get_taskinfo()
                break
        if not p==None:
            tasks.append(p)
            continue
        #_fixtask已空
        
        for k,v in _randomtask.items():
            if not v.is_assigned():#!!三分钟
                p=v.get_taskinfo()
                break
        if p==None:#randomtask也空了
            break
        else:
            tasks.append(p)
    
    #print 'get_task_state=%d'%get_task_state()
    print '%d fix remain , %d random remain'%(len(_fixtask),len(_randomtask))
    return tasks

def clear_task():
    _fixtask.clear()
    _randomtask.clear()
    
def get_fixtask():
    return _fixtask

def get_randomtask_id():
    global _randomtask_id
    _randomtask_id+=1
    return _randomtask_id

def add_randomtask(id,data):
    global _randomtask
    _randomtask[id]=data
    
def get_task_stat():
    return 'next %.0f s  %s</br></br>%d fix, %d random</br></br>%s</br></br>%s'%(_next_assign_time-time.time(),get_task_state(),len(_fixtask),len(_randomtask),_fixtask.__repr__(),_randomtask.__repr__())
    
def submit_fixtask(data):
    if data['task_info']['success']:
        error=''
        ftid=data['task_info']['task_id']
        try:
            self_param=json.dumps(data['task_info']['self_param'])
            ft= FixTask.objects.get(pk=ftid)
            ft.param=self_param
            ft.error_count=0
            ft.submit_times+=1
            ft.message_count+=len(data['message'])
            ft.last_submit_time=datetime.datetime.now()
            ft.save()
            _fixtask.pop(ftid)
        except Exception,e:
            errorstr='Add FixTask Result Error='+str(e)
            error+='['+errorstr+']'
            print errorstr
            if _fixtask[ftid].retry_times>2:
                #如果重试3次了,报警
                print 'fixtask %d failed 3 times,pop it'%ftid
                _fixtask.pop(ftid)
        
        for m in data['message']:
            if m['state']:#直接就是终态
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
                    #print 'json.dumps(m=',json.dumps(m['data'], ensure_ascii=False)
                    post_message(rt.pre_result)
                except Exception,e:
                    errorstr='Add FixTask_RandomTask Result Error='+str(e)
                    print 'ERROR URL=',m['data']['Url']
                    error+='['+errorstr+']'
                    print errorstr
                    continue
            else:#非终态，续进一步分配任务，加入_randomtask
                id=get_randomtask_id()
                t={}
                t['id']=id
                t['fxitask_id']=data['task_info']['task_id']
                t['business_id']=data['task_info']['business_id']
                t['parser_id']=None if data['task_info']['next_parser_id']==0 else data['task_info']['next_parser_id']
                t['pre_parser_id']=data['task_info']['cur_parser_id']
                t['state']=m['state']
                t['pre_result']=m['data']
                t['param']=m['param'] if m.has_key('param') else {}
                _randomtask[id]=Mem_RandomTask(t)
                _is_running=True
        echo='success' if error=='' else error
        return HttpResponse(echo)
    else:
        #处理错误信息
        ft=FixTask.objects.get(id=data['task_info']['task_id'])
        if ft.error_count>4:
            #连续异常5次向开发者报警
            #ft.error_count=0
            pass
        else:
            ft.error_count=ft.error_count+1
        ft.save()
        return HttpResponse('failed '+data['task_info']['error'])

def submit_randomtask(data):
    if data['task_info']['success']:
        error=''
        for m in data['message']:
            #print m['data']
            try:
                t=_randomtask[m['id']]
                pre_result=t.pre_result
                
                keys=m['data'].keys()
                for k in keys:
                    if m['data'][k]=='' and pre_result.has_key(k):
                        m['data'][k]=pre_result[k]
                
                #print 'parser_id=',data['task_info']['cur_parser_id']
                rt=RandomTask(business_id=data['task_info']['business_id'],
                          fixtask_id=t.fixtask_id,
                          parser_id=data['task_info']['cur_parser_id'],
                          pre_parser_id=data['task_info']['cur_parser_id'],
                          url=m['data']['Url'],
                          state=m['state'],
                          pre_result=json.dumps(m['data'], ensure_ascii=False),
                          last_submit_time=datetime.datetime.now())
                rt.save()
                _randomtask.pop(m['id'])
                post_message(m['data'])
            except Exception,e:
                if _randomtask[m['id']].retry_times>2:
                    #如果重试3次了,报警
                    print 'fixtask %d failed 3 times,pop it'%m['id']
                    _randomtask.pop(m['id'])
                errorstr='Update RandomTask Error='+str(e)
                error+='['+errorstr+']'
                print error
                continue
        echo='success' if error=='' else error
        return HttpResponse(echo)
    else:
        if _randomtask[data['task_info']['task_id']].retry_times>2:
            #如果重试3次了,报警
            print 'fixtask %d failed 3 times,pop it'%data['task_info']['task_id']
            _randomtask.pop(data['task_info']['task_id'])
        _randomtask[data['task_info']['task_id']].last_assign_time=0
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
            print message['Url']
        
        data={'json_str':json_str.encode('utf-8',errors='ignore')}
        #print data
        echo=post(post_url, data)
        print 'post_message success!'
        #print message
        return True
    except Exception,e:
        print 'post_message error=%s'%(str(e))
        print message
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
    
class Mem_FixTask(object):
    
    def __init__(self,ft):
        self.id=ft.id
        self.parser_id=ft.parser_id if ft.parser_id!=None else 0
        self.next_parser_id=ft.next_parser_id if ft.next_parser_id!=None else 0
        self.business_id=ft.business_id
        self.url=ft.url
        self.param={} if ft.param=='' or ft.param==None else json.loads(ft.param)
        self.last_assign_time=0
        self.interval=ft.interval
        self.submit_time=datetime.datetime.now()
        self.retry_times=0
        #self.state=0#1任务已分配，2任务已完成
        
    def get_taskinfo(self):
        p={}
        p['parser_id']=self.parser_id
        p['param']="'FixTask',%d,%d,%d,'%s',**%s"%(self.id,self.business_id,self.next_parser_id,self.url,self.param)
        self.last_assign_time=time.time()
        self.retry_times+=1
        return p
    
    def is_assigned(self):
        if time.time()-self.last_assign_time>180:
            return False
        else:
            return True
        
class Mem_RandomTask(object):
    
    def __init__(self,t):
        self.id=t['id']
        self.fixtask_id=t['fxitask_id']
        self.parser_id=t['parser_id']
        self.pre_parser_id=t['pre_parser_id']
        self.next_parser_id=0
        self.business_id=t['business_id']
        self.url=t['pre_result']['Url']
        self.param=t['param']
        self.state=t['state']
        self.pre_result=t['pre_result']
        self.last_assign_time=0
        self.interval=180
        self.retry_times=0
    
    def get_taskinfo(self):
        p={}
        p['parser_id']=self.parser_id
        p['param']="'RandomTask',%d,%d,%d,'%s',**%s"%(self.id,self.business_id,self.next_parser_id,self.url,self.param)
        self.last_assign_time=time.time()
        self.retry_times+=1
        return p
    
    def is_assigned(self):
        if time.time()-self.last_assign_time>180:
            return False
        else:
            return True
    def __str__(self):
        return '[%d]%s'%(self.id,self.url)
    