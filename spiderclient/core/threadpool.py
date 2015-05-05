#-*- encoding: utf-8 -*-
'''
Created on 2011-11-4

@author: Leo
'''
import Queue,time,sys
from spiderthread import SpiderThread
from utils.log import *
import setting

class ThreadPool(object):
    
    def __init__( self, pool_size=setting.THREAD_NUM):
        self.pool_size=pool_size
        self.thread_count =0
        self.threads = []
        self.pool_timeout=setting.TASKGROUPNUM*30 if setting.TASKGROUPNUM*30<200 else 200
        
    def __clear_pool(self):
        '''
                    清空线程池
        '''
        for t in self.threads:
            t.running=False
            #print '---ending thread '+str(t.id)
        del self.threads[:]
    
    def __kill_thread(self,t):
        '''
                    杀死一个线程
        '''
        t.running=False
        del t
        
    def __fill_pool(self,taskQueue,resultQueue,size=setting.THREAD_NUM):
        '''
                    生成线程填满线程池
        '''
        self.__clear_pool()
        for i in range(size):
            self.thread_count +=1
            thread = SpiderThread(self.thread_count, taskQueue, resultQueue )
            self.threads.append(thread)
    
    def __wait_for_complete( self):
        ''' wait for each of them to terminate'''
        starttime=time.time()
        while len(self.threads):
            thread = self.threads.pop()
            thread.join(2) 
            if (time.time()-starttime)>self.pool_timeout:
                self.__clear_pool()
                msg="[%s.%s %d]%s"%(self.__class__.__name__, sys._getframe().f_code.co_name,\
                        sys._getframe().f_lineno,'thread pool time out'+str(self.pool_timeout))
                warn(msg)
                break
            if thread.isAlive():
                self.threads.append( thread )
            else:
                thread.running=False
                #print '--ending thread '+str(thread.id)
                del(thread)
        else:
            print 'All task are are completed.'
        
    def execute(self,task_queue,result_queue):
        ''' the get-some-work, do-some-work main loop of worker threads '''
        if task_queue.qsize()==0:
            return
        elif task_queue.qsize()<setting.THREAD_NUM:
            THREAD_NUM=task_queue.qsize()
        else:
            THREAD_NUM=setting.THREAD_NUM
        
        self.__fill_pool(task_queue,result_queue,size=THREAD_NUM)
        print '-thread pool start'
        for t in self.threads:
            t.running=True
            t.start()
            #print '--running thread '+str(t.id)
        self.__wait_for_complete()
        print '-thread pool end'
        
        
if __name__ == '__main__':
    tp=ThreadPool()
    
    q=Queue.Queue()
    rq=Queue.Queue()
    q.put([u'Photograph_Fengniao_All_Detail', u'Photograph_Fengniao_All_Detail', u"'RandomTask',5266,1,2,0,'http://www.fengniao.com/secforum/1279693.html',**{u'post_id': 1279693, u'post_time': u'2011-11-04 19:17:00'}"])
    q.put([u'Photograph_Fengniao_All_Detail', u'Photograph_Fengniao_All_Detail', u"'RandomTask',5280,1,2,0,'http://www.fengniao.com/secforum/1279764.html',**{u'post_id': 1279764, u'post_time': u'2011-11-04 20:41:00'}"])
    q.put([u'Photograph_Fengniao_All_Detail', u'Photograph_Fengniao_All_Detail', u"'RandomTask',5281,1,2,0,'http://www.fengniao.com/secforum/1279765.html',**{u'post_id': 1279765, u'post_time': u'2011-11-04 20:41:00'}"])
    q.put([u'Photograph_Fengniao_All_Detail', u'Photograph_Fengniao_All_Detail', u"'RandomTask',5282,1,2,0,'http://www.fengniao.com/secforum/1279767.html',**{u'post_id': 1279767, u'post_time': u'2011-11-04 20:42:00'}"])
    q.put([u'Photograph_Fengniao_All_Detail', u'Photograph_Fengniao_All_Detail', u"'RandomTask',5283,1,2,0,'http://www.fengniao.com/secforum/1279770.html',**{u'post_id': 1279770, u'post_time': u'2011-11-04 20:45:00'}"])
    q.put([u'Photograph_Fengniao_All_Detail', u'Photograph_Fengniao_All_Detail', u"'RandomTask',5284,1,2,0,'http://www.fengniao.com/secforum/1279771.html',**{u'post_id': 1279771, u'post_time': u'2011-11-04 20:47:00'}"])
    tp.execute(q,rq)
    
    print 'rq.qsize() =',rq.qsize()
    
    while rq.qsize()>0:
        print rq.get()['task_info']
