#-*- encoding: utf-8 -*-

import uuid,datetime,json,time,random
import pylibmc
from models import *

_task_assign_num=5
_task_timeout=150

class RunningStatus(object):

    def __init__(self):

        pass

    def get_running_step(self):
        mc = pylibmc.Client()
        value = mc.get("running_step")

        if value<1:
            return value
        else:
            #sae上memcache值不能设为0，设为0就删除这个key了
            mc.set("running_step", 1)
            return 1

    def set_running_step(self,value):
        mc = pylibmc.Client()
        if value==0:
            return False
        else:
            mc.set("running_step", value)
            return True

#memcache的set操作
def _set_mc(key,value):
    mc = pylibmc.Client()
    mc.set(key, value)

#memcache的get操作
def _get_mc(key):
    mc = pylibmc.Client()
    return mc.get(key)

def init_mc():
    mc = pylibmc.Client()
    mc.set("running_step", 0)
    mc.set("spider_count", 0)
    mc.set("last_submit", 0)
    mc.set("last_run", 0)
    mc.set("next_assign_time", time.time())


#----------------------------------------------运行状态相关---------------------------------
#任务调度状态1,2,3
def get_running_step():
    value=_get_mc("running_step")
    if value<0 or type(value) is not int:
        value=0
        _set_mc("running_step",value)
    return value

def set_running_step(value):
    if type(value) is not int:
        value=0
    _set_mc("running_step",value)

#爬虫节点数
def get_spider_count():
    r=_get_mc("spider_count")
    if type(r) is not int:
        r=0
        _set_mc("spider_count",r)
    return r

def set_spider_count(value):
    if type(value) is not int:
        value=0
    _set_mc("spider_count",value)

def inc_spider_count():
    mc = pylibmc.Client()
    v=mc.get("spider_count")
    if type(v) is not int:
        _set_mc("spider_count",0)
    else:
        mc.incr("spider_count")

def clear_spider_count():
    _set_mc("spider_count",0)

#下次运行时间
def get_next_assign_time():
    r=_get_mc("next_assign_time")
    if not r or type(r) is not int:
        r=int(time.time())
        _set_mc("next_assign_time",r)
    return r

def set_next_assign_time(value):
    if type(value) is float:
        value=int(value)
    elif type(value) is not int:
        value=int(time.time())
    _set_mc("next_assign_time",value)

def get_assign_gap():
    i=get_next_assign_time()-time.time()
    return int(i)

#最后一条信息提交时间
def get_last_submit():
    v=_get_mc("last_submit")
    if type(v) is int:
        return datetime.datetime.fromtimestamp(v).strftime('%Y-%m-%d %H:%M:%S')
    else:
        return str(v)

def update_last_submit():
    _set_mc("last_submit",int(time.time()))

#最后爬虫执行任务时刻
def get_last_run():
    v=_get_mc("last_run")
    if type(v) is int:
        return datetime.datetime.fromtimestamp(v).strftime('%Y-%m-%d %H:%M:%S')
    else:
        return str(v)

def update_last_run():
    _set_mc("last_run",int(time.time()))

#--------------------------------------------任务相关--------------------------------------
#操作fixtask队列
def push_fixtask():
    tasks={}
    try:
        fixtask_list = FixTask.objects.filter(enable=True,
            last_assign_time__lt=datetime.datetime.now()-datetime.timedelta(seconds=_task_timeout)).order_by('-id')
        #fixtask_list = FixTask.objects.all().order_by('-id')
        for t in fixtask_list:
            if datetime.datetime.now()-t.last_submit_time>datetime.timedelta(seconds=get_interval(t.interval)):#get_interval(t.interval)
                t.assign_times+=1
                t.last_assign_time=datetime.datetime.now()
                t.save()

                parser_id=t.parser_id if t.parser_id is not None else 0
                next_parser_id=t.next_parser_id if t.next_parser_id is not None else 0
                self_param={} if t.param=='' or t.param is None else json.loads(t.param)

                param="'FixTask',%d,%d,%d,'%s',%d,**%s"%(t.id,t.business_id,next_parser_id,t.url,t.assign_times,self_param)
                tasks[parser_id]={'assgin_time':0,'status':'waiting','retry_times':0,'param':param}

        _set_mc("fixtask",tasks.__repr__())
    except Exception,e:
        r={0:str(e)}
        _set_mc("fixtask",r.__repr__())


def pop_fixtask(count):
    s=_get_mc("fixtask")
    ret=[]
    #线程不安全，脏数据
    try:
        task_list=eval(s)
        for k,t in task_list.items():
            if t['retry_times']>2:
                #重试3次失败，写数据库，报警
                task_list.pop(k)
                continue
            if time.time()-t['assgin_time']>_task_timeout:
                t['status']='running'
                t['assgin_time']=time.time()
                t['retry_times']+=1
                ret.append(t['param'])
                if len(ret)<count:
                    continue
                else:
                    break

        _set_mc("fixtask",task_list.__repr__())
        return ret
    except Exception,e:
        return str(e)

def clear_fixtask():
    _set_mc("fixtask",'{}')

#操作randomtask队列
def add_randomtask():
    pass

def pop_randomtask(count):
    pass

def clear_randomtask():
    _set_mc("randomtask",'{}')


def pop_task():
    tasks=pop_fixtask(_task_assign_num)
    if len(tasks)<_task_assign_num:
        tasks+=pop_randomtask(_task_assign_num-len(tasks))
    if len(tasks)<_task_assign_num:
        set_running_step(2)
    return random.sample(tasks, len(tasks))

#----------------------------------------------spider node manager---------------------------------
#新增一个spider
def add_spider(token,ip,machine_name):
    snlist=SpiderNode.objects.filter(token=token)
    try:
        if len(snlist):
            sn=snlist[0]
            sn=SpiderNode.objects.get(token=token)
            sn.machine_name=machine_name
            sn.ip=ip
            sn.login_times+=1
            sn.last_login_time=datetime.datetime.now()
            sn.last_assign_time=datetime.datetime.now()
            sn.save()
        else:
            sn=SpiderNode(token=token,
                name=machine_name,
                machine_name=machine_name,
                login_times=1,
                ip=ip,
                last_login_time=datetime.datetime.now(),
                last_assign_time=datetime.datetime.now()
            )
            sn.save()
    except Exception,e:
        raise

    
#取得正在工作的spider信息
def get_spiders_info():
    return {}

#当spider还活着时更新last_request
def update_live_spider(token):
    try:
        sn=SpiderNode.objects.get(token=token)
        if sn is None:
            return
        work_minute=(datetime.datetime.now()-sn.last_assign_time).seconds/float(60)
        sn.total_work_time+=round(work_minute,2)
        sn.last_assign_time=datetime.datetime.now()
        sn.save()
    except Exception,e:
        pass

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