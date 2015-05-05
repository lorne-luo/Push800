#-*- encoding: utf-8 -*-
'1'#version of parser file

import urllib2,urllib,os,copy,sys,traceback
import time,datetime,json,re
from utils import unistr
import utils.city as cityparser
from core.module_manager import *
from core.spider import BaseSpider,spiderlock
import utils.brand as brand

class Photograph_Taobao_List(BaseSpider):
    '''
            此Parse的解释
    '''

    def __unicode__(self):
        '''返回parser的名称，便于识别'''
        return "[%d]Taobao@%s" % (self.cur_parser_id,self.task_id)

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
            content_div=soup.find("ul", { "class" : "list-box" })
            item_list=content_div.findAll("li")
            for item in item_list:
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
                posttime=datetime.datetime.fromtimestamp(0)

                attribute_ul=item.find("ul", { "class" : "attribute" })
                if attribute_ul is None:
                    continue
                timestr=attribute_ul.find("li", { "class" : "pub-time" }).text
                if timestr.find('分钟')>-1:
                    timestr=timestr[:timestr.find('分钟')]
                    posttime=datetime.datetime.now()-datetime.timedelta(seconds=int(timestr)*60)
                elif timestr.find('小时')>-1:
                    timestr=timestr[:timestr.find('小时')]
                    if int(timestr)>6:
                        break#超过6小时的信息不采集
                    else:
                        posttime=posttime-datetime.timedelta(seconds=int(timestr)*3600)
                else:
                    #unknow condition
                    continue

                if posttime<=last_post_time:
                    #上一次已经爬行到这里
                    break
                else:
                    msg['Time']=posttime.strftime('%Y-%m-%d %H:%M:%S')

                price_li=attribute_ul.find("li", { "class" : "price" })
                if not price_li is None:
                    pricestr=price_li.text
                    pricestr=unistr.extract_number(pricestr)
                    msg['Price']=int(float(pricestr))

                seller_div=item.find("div", { "class" : "seller" })
                if not seller_div is None:
                    seller_li=seller_div.find("li", { "class" : "seller-nick" })
                    if not seller_li is None:
                        msg['Seller']=seller_li.find("a")['title']

                    city_li=seller_div.find("li", { "class" : "seller-area" })
                    if not city_li is None:
                        citystr=city_li.text
                        if citystr.find(u'上海')>-1:
                            msg['City']=u'上海'
                        elif citystr.find(u'北京')>-1:
                            msg['City']=u'北京'
                        elif citystr.find(u'广州')>-1:
                            msg['City']=u'广州'
                        elif citystr.find(u'深圳')>-1:
                            msg['City']=u'深圳'
                        elif citystr.find(u'天津')>-1:
                            msg['City']=u'天津'
                        c=cityparser.extract_city(msg['City'])
                        msg['City_id']=c[0]

                        districtstr=citystr.replace(msg['City'],'').strip()
                        if districtstr!='':
                            msg['District']=districtstr

                pass


                title_tag=item.find("h3", { "class" : "item-title" })
                if title_tag is None:
                    continue
                msg['Url']=title_tag.find("a")['href']
                quality_tag=title_tag.find("span")
                if not quality_tag is None:
                    quality_str=quality_tag.text
                    if quality_str.find(u'全新')>-1:
                        msg['Quality']=100
                    else:
                        #TODO quality<100
                        quality_str=unistr.extract_number(quality_str)
                        if quality_str>'':
                            quality=int(quality_str)
                            if quality<10:
                                msg['Quality']=quality*10
                            else:
                                msg['Quality']=quality
                        pass
                    msg['Title']=unicode(quality_tag.nextSibling).strip()

                pic_div=item.find("div", { "class" : "item-photo*" })
                msg['Pics']=[]
                if not pic_div is None:
                    pic_img=pic_div.find("img")
                    if not pic_img is None:
                        msg['Pics'].append(pic_img['src'])






                #state=0 if content.endswith('…') else 1
                '''
                                            解析完毕将msg加入队列
                state:任务状态，1已完成，0需继续处理
                id：新纪录置None或者0，老纪录置self.task_id
                '''
                message={'data':msg,'state':0,'id':0}
                self.message.append(message)

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

    p=Photograph_Taobao_List('FixTask',4,1,0,'http://s.ershou.taobao.com/list/list.htm?catid=50025242&divisionId=110100',123,\
                         **{"last_post_time": "2012-05-10 13:11:02", 'last_post_url':'http://ershou.taobao.com/item.htm?id=14686333680&from=list&similarUrl=http://s.ershou.taobao.com/list/json_list.htm?catid=50025242%26divisionId=110100'})
    r=p.run()
    print r
    print len(r['message'])
    for m in r['message']:
        print m['data']['Url'],m['data']['Time']
