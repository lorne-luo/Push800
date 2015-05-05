#-*- encoding: utf-8 -*-
'''
from SpiderTask import *
from SpiderBusiness.business import *

businessList=[]
businessList.append(SpiderBusiness(1,'Photograph',[1,2,3],'PhotographMessage'))
businessList.append(SpiderBusiness(2,'Mobile',[4,5],'MobileMessage'))

for b in businessList:
    print b.id,b.name,b.spiderTask,b.messageType



'''
     
import threading
import time

class thrA(threading.Thread):
    def __init__(self,str):
        self.str = str
        threading.Thread.__init__(self)
        
    def run(self):
        for i in range(5):
            print str(i+1)+"A"
            print self.str
            time.sleep(2)
        
class thrB(threading.Thread):
    def __init__(self,str):
        self.str =str
        threading.Thread.__init__(self)
    
    def run(self):
        for i in range(5):
            print str(i+1)+"B"
            print self.str
            time.sleep(1)
        
        
if __name__=="__main__":
      threadA = thrA("I am A")
      threadB = thrB("I am B")
      threadD = thrB("I am D")
      threadC = thrA("I am C")
      
      
      threads=[threadA,threadB,threadC,threadD]
      threadA.start()
      threadB.start()
      threadC.start()
      threadD.start()
      while len(threads):
          for t in threads:
              t.join(2)
              if not t.isAlive():
                  threads.remove(t)
                  print t.str+' deaded'
              else:
                  print t.str+' still living'


      print "end"


