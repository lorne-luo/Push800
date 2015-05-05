#-*- encoding: utf-8 -*-
import Queue, threading, sys, time, json,datetime,urllib2,uuid
import socket
from business.business import * 
from business.message import *
from core.threadpool import ThreadPool
from core.spiderthread import SpiderThread
from core.scheduler import Scheduler
from core.module_manager import *
from utils.network import post
import setting


businessList={1:'Photograph',2:'Mobile'}

tasklist=[(1,'http://www.fengniao.com/secforum/search.php?bsid=2&stid=2&ptypeid=2&tkey=&sortorder=&daysprune=&sortfield=posttime','Photograph_Fengniao_All_List',1317027685)]
tasklist.append((1,'http://www.fengniao.com/secforum/search.php?bsid=2&stid=2&ptypeid=2&tkey=&sortorder=&daysprune=&sortfield=posttime','Photograph_Fengniao_All_List',1317027685))

#node启动时向server注册    
def spider_login():
    #uid=uuid.uuid5(uuid.NAMESPACE_DNS, setting.SPIDER_NAME)
    node = uuid.getnode()
    
    info={}
    info['macint']=node
    info['machine_name']=setting.SPIDER_NAME
    
    data = {'login_data':json.dumps(info, ensure_ascii=False)}
    resp = post(setting.SPIDER_LOGIN_URL, data)
    print 'login to %s'%setting.BASE_URL
    loginresp=json.loads(resp)
    if loginresp['success']:
        load_all_module(loginresp['modules'])
        setting.TOKEN=loginresp['token']
        print 'login success , server token = %s'%(loginresp['token'])
    else:
        print 'login failed , error=%s'%(loginresp['error']) 
    return loginresp['success']
    
if __name__ == '__main__':
    print 'INTER_IP_ADDRESS=',setting.INTER_IP_ADDRESS
    print 'SPIDER_NAME=',setting.SPIDER_NAME
    socket.setdefaulttimeout(setting.HTTP_TIMEOUT)
    
    try:
        if not spider_login():
            sys.exit(-1)
    except Exception,e:
        print 'spider login failed=%s'%(str(e))
        sys.exit(-1)
    
    scheduler=Scheduler()
    threadpool=ThreadPool()
    
    #sys.exit(-1)
    print ''
    while True:
        print ''
        starttime=time.time()
        print '%s start running'%(time.strftime('%H:%M:%S'))
        scheduler.get_tasklist()
        
        if scheduler.get_taskcount()>0:
            threadpool.execute(scheduler.taskQueue, scheduler.resultQueue)
            #这里处理resultQueue
            scheduler.clear_result()
            print 'end running'
            print '%s TimeCost=%.3f Count=%d'%(time.strftime('%H:%M:%S'),time.time()-starttime,setting.COUNT)
        else:
            setting.COUNT=setting.COUNT+1
            update_module()
            print 'no task, end running, sleep %d s , %s'%(scheduler.sleep_seconds,\
                    (datetime.datetime.now()+datetime.timedelta(seconds=scheduler.sleep_seconds)).strftime('%H:%M:%S'))
            print '%s TimeCost=%.3f Count=%d'%(time.strftime('%H:%M:%S'),time.time()-starttime,setting.COUNT)
            
            time.sleep(scheduler.sleep_seconds)
            

    #s=SpiderClient(config.THREADNUM,config.TIMEOUT)
    #s.run()
    