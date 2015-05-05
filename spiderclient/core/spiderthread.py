#-*- encoding: utf-8 -*-
import Queue,time,json,sys
from threading import Thread
from utils.network import post
from utils.log import *
from core.module_manager import *
import setting

#from SpiderTask.Photograph_Fengniao_All_Detail import * 
#from SpiderTask.Photograph_Fengniao_All_List import * 
 
class SpiderThread(Thread):
    
    def __init__( self,id, taskQueue, resultQueue, **kwds):
        Thread.__init__( self, **kwds )
        self.id = id
        self.setDaemon( True )
        self.taskQueue = taskQueue
        self.resultQueue = resultQueue
        self.timeout = 5
        self.running=True

    def run( self ):
        ''' the get-some-work, do-some-work main loop of worker threads '''
        while self.running:
            try:
                t=self.taskQueue.get(timeout=self.timeout)
                #exec('from spiders.'+s[0]+' import *')
                #starttime=time.time()
                #r=eval(s[1]+'('+s[2]+')')
                #r['run_info']['time_cost']=time.time()-starttime
                #exec('from spiders.'+t[0]+' import '+t[1])
                
                parser=get_spider(t[0])
                if parser==None:
                    raise Exception('spider parser==None , the parser_id='+str(t[0]))
                p=eval('parser('+t[1]+')')
                result=p.run()
                
                self.resultQueue.put(result)
                #print '[POST]='+json.dumps(result, ensure_ascii=False)
                data = {'submit':result['task_info']['task_type'],'result':json.dumps(result, ensure_ascii=False)}
                echo = post(setting.SUBMIT_TASK_URL, data)
                print '---%s %s %d=%s,P=%d D=%dB C=%.3fs'%(time.strftime('%H:%M:%S'),unicode(p),len(result['message']),echo,\
                    result['run_info']['page_count'],result['run_info']['data_trans'],\
                    result['run_info']['download_duration']+result['run_info']['parse_duration'])
            except Queue.Empty:
                self.running=False
                break
            except Exception,e:
                msg="[%s.%s %d] %s : %s"%(self.__class__.__name__, sys._getframe().f_code.co_name,\
                        sys._getframe().f_lineno,type(e).__name__,str(e))
                err(msg)
                continue

if __name__ == '__main__':
    load_all_module()
    t=(7, u"'RandomTask',1260,1,0,'http://gz.ganji.com/shuma/11112520_2029198.htm',1,**{}")
    parser=get_spider(t[0])
    p=eval('parser('+t[1]+')')
    p2=eval('parser('+t[1]+')')
    p2.id=12352
    result=p.run()
    print parser.version,p.version
    print parser.id,p.id,p2.id
    #print result
    data = {'submit':result['task_info']['task_type'],'result':json.dumps(result, ensure_ascii=False)}
    echo = post(setting.SUBMIT_TASK_URL, data)
    print echo
    
