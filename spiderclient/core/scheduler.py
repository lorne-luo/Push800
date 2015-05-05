#-*- encoding: utf-8 -*-
'''
任务调度、获取任务、返回任务结果

Created on 2011-11-4

@author: Leo
'''
import Queue,urllib2,json,sys,traceback,os,threading,time
import socket
from utils.log import *
from utils.network import post
import setting

class Scheduler(object):
    def __init__( self):
        #业务相关，任务信息的队列
        self.taskQueue = Queue.Queue()
        #业务相关，任务结果的队列
        self.resultQueue = Queue.Queue()
        #从服务器取得的任务队列原始信息，后会加入self.taskQueue供线程池执行
        self.tasklist=None
        self.sleep_seconds=setting.DEFAULT_SLEEPING_TIME
        
    def clear_task(self):
        '''
                    清空所有任务
        '''
        while not self.taskQueue.empty():
            self.taskQueue.get()
    
    def clear_result(self):
        '''
                    清空所有结果
        '''
        while not self.resultQueue.empty():
            self.resultQueue.get()
            
    def add_task(self, task):
        '''
                    新添一个任务
        '''
        self.taskQueue.put(task)  
        
    def get_task(self):
        '''
                    获取一个任务
        '''
        try:
            return self.taskQueue.get(timeout=setting.QUEUE_TIMEOUT)
        except Queue.Empty:
            return None
        
    def get_taskcount(self):
        '''
                    获取一个任务
        '''
        return self.taskQueue.qsize()
    
    def get_tasklist(self):
        self.clear_task()
        self.clear_result()
        self.tasklist=None
        data=None
        try:
            token = {'token':setting.TOKEN}
            #token = {'token':'bfd78652-7694-5cc3-94a7-a20588e766ce'}
            spiderinfo={'spiderinfo':json.dumps(token, ensure_ascii=False)}
            data = post(setting.GET_TASK_URL, spiderinfo)
            self.tasklist=json.loads(data)
        except Exception,e:
            #，json格式不对
            info = sys.exc_info()
            print "**%s:%s" % info[:2]
            file, lineno, function, text = traceback.extract_tb(info[2])[0]
            msg = "%s:%s@%s line%s %s(),%s"%(info[0],info[1],os.path.split(file)[1],lineno,function,str(data))
            err(msg)
        
        #请求任务列表可能有两种信息返回
        #如果是个字典则是一些控制信息，比如sleep时间
        #如果是一个[]则是新的任务
        try:
            #如果是个字典则是一些控制信息，比如sleep时间
            if type(self.tasklist) is dict:
                ss=self.tasklist['sleep_seconds']
                if type(ss) is int and ss>0:
                    self.sleep_seconds=ss
                else:
                    print 'response sleep_seconds error , setting.DEFAULT_SLEEPING_TIME=',setting.DEFAULT_SLEEPING_TIME
                    self.sleep_seconds=setting.DEFAULT_SLEEPING_TIME
            #如果是一个[]则是新的任务
            elif type(self.tasklist) is list:
                for t in self.tasklist:
                    task=[t['parser_id'],t['param']]
                    #print t['param']
                    self.add_task(task)
            else:
                print 'gettasks return json err , data='+\
                        str(type(self.tasklist))+'\n'+self.tasklist.__repr__()
        except Exception,e:
            info = sys.exc_info()
            print "**%s:%s" % info[:2]
            file, lineno, function, text = traceback.extract_tb(info[2])[0]
            msg = "%s:%s@%s line%s %s(),%s"%(info[0],info[1],os.path.split(file)[1],lineno,function,str(data))
            err(msg)
        
        print '-get task count =',self.taskQueue.qsize()
        return self.taskQueue.qsize()
    
class GetTaskThread(threading.Thread):
    #返回结果通过tl传入
    def __init__(self,**kwds):
        #super(GetTaskThread,self).__init__( self, **kwds )
        threading.Thread.__init__( self, **kwds )
        self.setDaemon( True )
        self.tasklist=None
        
    def run( self ):
        '''获取任务列表'''
        try:
            #token = {'token':setting.TOKEN}
            token = {'token':345052807176}
            #token = {'token':'bfd78652-7694-5cc3-94a7-a20588e766ce'}
            spiderinfo={'spiderinfo':json.dumps(token, ensure_ascii=False)}
            data = post(setting.GET_TASK_URL, spiderinfo)
            self.tasklist=json.loads(data)
            #print id(self.tasklist),type(self.tasklist),self.tasklist,'in thread'
        except Exception,e:
            info = sys.exc_info()
            print "**%s:%s" % info[:2]
            file, lineno, function, text = traceback.extract_tb(info[2])[0]
            msg = "%s:%s@%s line%s %s(),%s"%(info[0],info[1],os.path.split(file)[1],lineno,function,str(data))
            err(msg)
            
    #timeout超时时间，若超时返回None
    def get_result(self):
        #print id(self.tasklist),'init'
        starttime=time.time()
        self.start()
        while True:
            self.join(2)
            if (time.time()-starttime)>setting.HTTP_TIMEOUT:
                msg="[%s.%s %d]%s"%(self.__class__.__name__, sys._getframe().f_code.co_name,\
                        sys._getframe().f_lineno,'get tasklist timeout='+str(setting.HTTP_TIMEOUT))
                warn(msg)
                break
            elif not self.isAlive():
                break
        return self.tasklist
    
if __name__ == '__main__':
    #s=Scheduler()
    #s.get_tasklist()
    
    tt=GetTaskThread()
    tasklist=tt.get_result()
    print id(tasklist),type(tasklist),tasklist
    
