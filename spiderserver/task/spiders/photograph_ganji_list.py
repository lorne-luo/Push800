#-*- encoding: utf-8 -*-
'1'#version of parser file

import urllib2,urllib,os,copy,sys,traceback
import time,datetime,json,re
import utils.city as cityparser
import utils.brand as brand
from core.module_manager import *
from core.spider import BaseSpider,spiderlock

class Photograph_Ganji_List(BaseSpider):
    '''
            此Parse的解释
    '''
    def __unicode__(self):
        city=self.url[7:9]
        return "[%d]Ganji@%s" % (self.cur_parser_id,city)

    '''
            基类成员变量说明
    self.task_type=task_type                                                        #任务类型
    self.task_id=task_id                                                            #任务ID
    self.business_id=business_id                                                    #业务ID
    self.cur_parser_id=self.id                                                      #当前parser ID
    self.next_parser_id=next_parser_id                                              #下一个parser ID
    self.url=url                                                                    #URL地址
    self.param=self_param                                                           #自管理的参数信息
    self.error=[]                                                                   #错误信息
    self.message=[]
    
    self.get_message_format()                 #根据businessid返回message消息的空结构
    self.download_page(url)                   #下载网页,返回其htmldom
    set_encoding(encode)                      #网页的编码格式，一般中文网页设为gb18030
    '''
    def parse(self,soup):
        '''
        soup为目标网页的htmldoc
        '''
        try:
            '''从self.param取出自管理参数'''
            last_post_url=self.param['last_post_url']
            #datetime.strptime()线程不安全，加锁,http://bugs.python.org/issue7980
            with spiderlock:
                last_post_time=datetime.datetime.strptime(self.param['last_post_time'],'%Y-%m-%d %H:%M:%S')
        except Exception,e:
            self.error.append('task[%d] Get self.param Error:%s'%(self.task_id,str(e)))
            print self.error
            print 'self.param=',self.param
            return

        baseurl=self.url[:self.url.find('.com')+4]

        try:
            '''对soup的解析过程'''
            divlist=soup.findAll("div", { "class" : "list" })
            div=divlist[0]

            ptags=div.findAll("p")
            for p in ptags:
                try:
                    '''
                                                    取得message的格式
                                                    具体格式见business.business模块的businessList
                    '''
                    msg=self.get_message_format()
                except Exception,e:
                    self.error.append('Get messge format Error:'+str(e))
                    print self.error
                    return

                timestr=p.find("i").text
               #if timestr==u'置顶' or timestr==u'推广':continue
                posttime=datetime.datetime.fromtimestamp(0)
                if timestr.endswith('分钟'):
                    timestr=timestr[:len(timestr)-2]
                    posttime=datetime.datetime.now()-datetime.timedelta(seconds=int(timestr)*60)
                elif timestr.endswith('小时'):
                    timestr=timestr[:len(timestr)-2]
                    if int(timestr)>6:
                        break#超过6小时的纪录不采集
                    else:
                        posttime=posttime-datetime.timedelta(seconds=int(timestr)*3600)
                else:
                    #跳过timestr==u'置顶' or timestr==u'推广'
                    continue

                atag=p.find("a")
                url=baseurl+atag['href']
                #print url
                if posttime<=last_post_time:
                    #上一次已经爬行到这里
                    break

                msg['Time']=posttime.strftime('%Y-%m-%d %H:%M:%S')
                msg['Url']=url
                msg['Title']=atag.text
                msg['Brand_id']=brand.extract_brand(msg['Title'])

                if url.startswith('http://sh.'):
                    msg['City']=u'上海'
                elif url.startswith('http://bj.'):
                    msg['City']=u'北京'
                elif url.startswith('http://gz.'):
                    msg['City']=u'广州'
                elif url.startswith('http://sz.'):
                    msg['City']=u'深圳'
                elif url.startswith('http://tj.'):
                    msg['City']=u'天津'

                c=cityparser.extract_city(msg['City'])
                msg['City_id']=c[0]

                span=p.find('span',{'class' : 'adr'})
                #msg['District']=span.text
                d=cityparser.extract_district(span.text)
                msg['District']=d[1]
                msg['District_id']=d[0]

                pricestr=span.nextSibling
                msg['Price']=pricestr[pricestr.find('- ')+2:pricestr.find('元')]


                #state=0 if content.endswith('…') else 1
                '''
                                            解析完毕将msg加入队列
                state:任务状态，1已完成，0需继续处理
                id：新纪录置None或者0，老纪录置self.task_id
                '''
                item={'data':msg,'state':0,'id':0}
                self.message.append(item)

            '''更新自管理参数'''
            if len(self.message)>0:
                self.param['last_post_url']=self.message[0]['data']['Url']
                self.param['last_post_time']=self.message[0]['data']['Time']
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
    #load_all_module()

    p=Photograph_Ganji_List('FixTask',6,1,0,'http://gz.ganji.com/shumaxiangji/',123,\
                            **{"last_post_time": "2012-05-08 07:39:53", 'last_post_url':'http://bj.ganji.com/shuma/236893602x.htm'})
    r=p.run()
    print r
    print len(r['message'])
    for m in r['message']:
        print m['data']['Url'], m['data']['Time']
    
    
    