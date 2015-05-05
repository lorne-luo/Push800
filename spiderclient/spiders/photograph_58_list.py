#-*- encoding: utf-8 -*-
'1'#version of parser file

import urllib2,urllib,os,copy,sys,traceback
import time,datetime,json,re
import utils.city as cityparser
from core.module_manager import *
from core.spider import BaseSpider,spiderlock
import utils.brand as brand

class Photograph_58_List(BaseSpider):
    '''
            此Parse的解释
    '''

    def __unicode__(self):
        '''返回parser的名称，便于识别'''
        city=self.url[7:9]
        return "[%d]58@%s" % (self.cur_parser_id,city)

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
            pass
        except Exception,e:
            self.error.append('task[%d] Get self.param Error:%s'%(self.task_id,str(e)))
            print self.error
            print 'self.param=',self.param
            return

        try:
            '''对soup的解析过程'''
            table=soup.find("table", { "class" : "tblist tiaozao" })
            trlist=table.findAll("tr")
            for tr in trlist:
                td=tr.findAll("td")
                if len(td)<2:continue

                try:
                    '''
                                                    取得message的格式
                                                    具体格式见business.business模块的businessList
                    '''
                    msg=self.get_message_format()
                except Exception,e:
                    self.error.append('task[%d] Get messge format Error:%s'%(self.task_id,str(e)))
                    print self.error
                    return

                timestr=td[0].text#10分钟
                posttime=datetime.datetime.fromtimestamp(0)

                if timestr.endswith('分钟'):
                    timestr=timestr[:len(timestr)-2]
                    posttime=datetime.datetime.now()-datetime.timedelta(seconds=int(timestr)*60)
                elif timestr.endswith('小时'):
                    timestr=timestr[:len(timestr)-2]
                    if int(timestr)>6:
                        break#超过6小时的信息不采集
                    else:
                        posttime=posttime-datetime.timedelta(seconds=int(timestr)*3600)
                else:
                    #跳过各种置顶帖
                    continue

                url=td[1].find("a")['href']
                #print url
                if posttime<=last_post_time:
                    #上一次已经爬行到这里
                    break
                msg['Url']=url
                msg['Title']=td[1].find("a").text
                if msg['Title'].find(u'求购')>-1:
                    continue
                msg['Brand_id']=brand.extract_brand(msg['Title'])

                if url[7:10]=='sh.':
                    msg['City']=u'上海'
                elif url[7:10]=='bj.':
                    msg['City']=u'北京'
                elif url[7:10]=='gz.':
                    msg['City']=u'广州'
                elif url[7:10]=='sz.':
                    msg['City']=u'深圳'
                elif url[7:10]=='tj.':
                    msg['City']=u'天津'

                c=cityparser.extract_city(msg['City'])
                msg['City_id']=c[0]

                msg['Time']=posttime.strftime('%Y-%m-%d %H:%M:%S')
                ul=td[1].find("ul")
                li=ul.findAll("li")
                for i in li:
                    if i.text.startswith('成色：'):
                        quality=i.text
                        quality=quality[3:]
                        if quality=='全新':
                            msg['Quality']='100'
                        else:
                            quality=quality[:len(quality)-2]
                            if len(quality)==1:
                                msg['Quality']=quality+'0'
                            else:
                                msg['Quality']=quality
                    elif i.text.startswith('价格：'):
                        price=i.text
                        price=price[3:]
                        if price=='面议':
                            msg['Price']=price
                        else:
                            price=price[:len(price)-1]
                        msg['Price']=price
                    elif i.text.startswith('地点：'):
                        #msg['District']=i.text[3:]
                        d=cityparser.extract_district(i.text[3:])
                        msg['District']=d[1]
                        msg['District_id']=d[0]

                content=td[1].find("p").text
                msg['Content']=td[1].find("p").text

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

    p=Photograph_58_List('FixTask',4,1,0,'http://bj.58.com/shumaxiangji/',123,\
                         **{"last_post_time": "2012-05-08 08:44:02", 'last_post_url':'http://bj.58.com/shuma/9774432020098x.shtml'})
    r=p.run()
    print r
    print len(r['message'])
    for m in r['message']:
        print m['data']['Url'],m['data']['Time']

    