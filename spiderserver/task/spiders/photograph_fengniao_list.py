#-*- encoding: utf-8 -*-
'1'#version of parser file

import urllib2,urllib,os,copy,sys,traceback
import time,datetime,json,re
import utils.city as cityparser
import utils.brand as brand

from core.spider import BaseSpider, spiderlock
from core.module_manager import *

class Photograph_Fengniao_List(BaseSpider):
    '''
            蜂鸟二手摄影器材交易版list页面,不区分城市
    http://www.fengniao.com/secforum/search.php?bsid=2&stid=2&ptypeid=2&tkey=&sortorder=&daysprune=&sortfield=posttime
    '''
    
    def __unicode__(self):
        return '[%d]Fengniao_List' % (self.cur_parser_id)

    def parse(self,soup):
        '''数据库中最后发帖时间和最后ID'''
        prelasttime=datetime.datetime.now()
        with spiderlock:
            prelasttime=datetime.datetime.strptime(self.param['last_post_time'],'%Y-%m-%d %H:%M:%S')
        prelastid=int(self.param['last_post_id'])
        '''记录新最后发帖时间的临时变量'''
        newlasttime=prelasttime
        newlastid=prelastid
    
        try:
            table=soup.find("table", { "class" : "mt10" })
            if table==None:
                print '    Warning:没有数据项'
                return
            i=0
            trlist=table.findAll("tr",limit=10)
            for tr in trlist:
                if i==0:
                    i=i+1
                    continue
                td=tr.findAll("td")
                
                '''更新两个自管理参数'''
                '''发帖时间'''
                with spiderlock:
                    posttime=datetime.datetime.strptime('20'+td[9].text,'%Y-%m-%d %H:%M')
                if posttime<=prelasttime:
                    #上一次已经爬行到这里
                    break
                else:
                    if posttime>newlasttime:
                        newlasttime=posttime
                '''帖子ID'''
                try:        
                    p=re.compile(r'\/(\d+).html$')
                    v = p.findall(td[2].find("a")['href'])
                    postid=int(v[0])
                except:
                    postid=0
                    
                if postid>newlastid:
                        newlastid=postid
                
                m=self.get_message_format()
                m['Time']=posttime.strftime('%Y-%m-%d %H:%M:%S')

                m['Title']=td[2].text
                if m['Title'].find(u'求购')>-1:
                    continue
                m['Brand_id']=brand.extract_brand(m['Title'])

                m['Url']=td[2].find("a")['href']
                m['Quality']=td[5].text
                m['Quality']=m['Quality'][:len(m['Quality'])-1]
                m['Price']=td[6].text[1:]

                c=cityparser.extract_city(td[4].text)
                m['City']=c[1]
                m['City_id']=c[0]


                message={'data':m,'state':0,'id':None}
                self.message.append(message)
        except Exception,e:
            self.error.append('[%s]%s parse error:%s'%(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),self.__class__.__name__,str(e)))
            info = sys.exc_info()
            print "Parser Error:* %s: %s" % info[:2]
            for file, lineno, function, text in traceback.extract_tb(info[2]):
                s='*%s,line %s,%s()'%(os.path.split(file)[1],lineno,function)
                self.error.append(s)
                print s
        
        '''list页面没有更新，沿ID爬行'''
        try:
            if len(self.message)==0:
                #下一个id str(prelastid+1) todo 改成循环
                self.next_parser_id=3#和业务相关了3是Photograph_Fengniao_All_Detail_ByID
                nextm={}
                for offset in range(20):
                    idnow=prelastid+offset+1
                    try:
                        Photograph_Fengniao_Detail_ByID=get_spider_byname('Photograph_Fengniao_Detail_ByID')
                        parser=Photograph_Fengniao_Detail_ByID('RandomTask',0,1,0,'http://www.fengniao.com/secforum/',self.assign_token,**{'post_id':idnow})
                        nextm=parser.run()
                        self.profiler['page_count']+=nextm['run_info']['page_count']
                        self.profiler['data_trans']+=nextm['run_info']['data_trans']
                        
                        if nextm['task_info']['success']:
                            self.message+=nextm['message']
                            if newlasttime < datetime.datetime.strptime(nextm['task_info']['self_param']['post_time'],'%Y-%m-%d %H:%M:%S'):
                                newlasttime=datetime.datetime.strptime(nextm['task_info']['self_param']['post_time'],'%Y-%m-%d %H:%M:%S')
                                
                            if idnow>newlastid:
                                newlastid=idnow
                            
                            print '---NextID='+str(idnow)+' Success'
                        else:
                            if 'NULL_PAGE' in nextm['task_info']['error']:
                                print '---NextID='+str(idnow)+' NULL_PAGE'
                                break
                            elif 'MERCHANT_PAGE' in nextm['task_info']['error']:
                                print '---NextID='+str(idnow)+' MERCHANT_PAGE'
                                continue
                            else:
                                print '---NextID='+str(idnow)+' '+nextm['task_info']['error'].__repr__()
                                continue
                    except Exception,e:
                        print '---NextID='+str(idnow)+' ErrinList:'+str(e)
                        self.error.append('---NextID='+str(idnow)+' ErrinList:'+str(e))
                        continue
                self.message.reverse()
                
            '''最后发帖时间'''   
            if not (newlasttime==prelasttime and newlastid==prelastid): 
                self.param['last_post_id']=newlastid
                self.param['last_post_time']=newlasttime.strftime('%Y-%m-%d %H:%M:%S')
            
            '''有新的帖子才更新参数'''
            if len(self.message)>0:
                self.message.reverse()
            self.success=True
        except Exception,e:
            self.error.append('[%s]%s parse error:%s'%(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),self.__class__.__name__,str(e)))
            info = sys.exc_info()
            print "Parser Error:* %s: %s" % info[:2]
            for file, lineno, function, text in traceback.extract_tb(info[2]):
                s='*%s,line %s,%s()'%(os.path.split(file)[1],lineno,function)
                self.error.append(s)
                print s

'''Test'''
if __name__ == '__main__':
    t=('photograph_fengniao_list','Photograph_Fengniao_List',"'FixTask',1,1,2,'http://www.fengniao.com/secforum/search.php?bsid=2&stid=2&ptypeid=2&tkey=&sortorder=&daysprune=&sortfield=posttime',123,**{u'last_post_id': 1288421, u'last_post_time': u'2011-11-14 16:09:00'}")
   
    exec('from spiders.'+t[0]+' import '+t[1])
    exec(t[1]+'.id=1')
    p=eval(t[1]+'('+t[2]+')')
    r=p.run()
    print r
    
    
    
    