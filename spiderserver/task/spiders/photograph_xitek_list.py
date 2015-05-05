#-*- encoding: utf-8 -*-
'1'#version of parser file

import urllib2,urllib,os,copy,sys,traceback
import time,datetime,json,re
from utils import unistr
import utils.city as cityparser
from core.module_manager import *
from core.spider import BaseSpider,spiderlock
import utils.brand as brand

class Photograph_Xitek_List(BaseSpider):
    '''
            此Parse的解释
    '''

    def __unicode__(self):
        '''返回parser的名称，便于识别'''
        return "[%d]Xitek@%s" % (self.cur_parser_id,self.task_id)

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
        last_post_time=datetime.datetime.now()
        try:
            '''从self.param取出自管理参数'''
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
            newlasttime=last_post_time
            content_div=soup.find("table", { "class" : "table1 margin-10" })
            item_list=content_div.findAll("tr")
            if item_list is None:
                return

            #跳过第一个tr
            count=0
            for item in item_list:
                count+=1
                if count==1:
                    continue
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

                td_list=item.findAll("td")
                if td_list is None or len(td_list)<10:
                    continue

                timestr='20'+td_list[9].text
                with spiderlock:
                    posttime=datetime.datetime.strptime(timestr,'%Y-%m-%d %H:%M')

                if posttime<=last_post_time:
                    #旧数据
                    continue
                else:
                    if posttime>newlasttime:
                        newlasttime=posttime
                msg['Time']=posttime.strftime('%Y-%m-%d %H:%M:%S')

                title_tag=td_list[2].find('a')
                if title_tag.text.find(u'求购')>-1:
                    continue
                else:
                    msg['Title']=title_tag.text
                msg['Url']=title_tag['href']
                msg['Brand_id']=brand.extract_brand(td_list[1].text)
                msg['Quality']=td_list[5].text.replace('%','')
                msg['Seller']=td_list[3].text
                msg['Price']=td_list[6].text

                c=cityparser.extract_city(td_list[4].text)
                msg['City']=c[1]
                msg['City_id']=c[0]






                #============================================================================
                '''
                解析完毕将msg加入队列
                state:任务状态，1已完成，0需继续处理
                id：新纪录置None或者0，老纪录置self.task_id
                '''
                message={'data':msg,'state':0,'id':0}
                self.message.append(message)

            '''更新自管理参数'''
            self.param['last_post_time']=newlasttime.strftime('%Y-%m-%d %H:%M:%S')
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

    p=Photograph_Xitek_List('FixTask',4,1,0,'http://www2.xitek.com/exchange/ex_search.php?exchangetype=1&partid=0&ex_kindid=0&provinceid=1&cityid=0&exstate=1&query=&searchin=0&exthread_dateline=7&search_order=1&username=&action=dosearch',123,\
                         **{"last_post_time": "2012-05-10 13:11:02"})
    r=p.run()
    print r
    print len(r['message'])
    for m in r['message']:
        print m['data']['Url'],m['data']['Time']
