#-*- encoding: utf-8 -*-
'1'#version of parser file

import urllib2,urllib,os,copy,sys,traceback
import time,datetime,json,re
from utils import unistr
import utils.city as cityparser
from utils.BeautifulSoup import NavigableString, Tag, BeautifulSoup
import utils.brand as brand
from core.module_manager import *
from core.spider import BaseSpider

class Photograph_Xitek_Detail(BaseSpider):
    '''
    此Parse的解释
    '''

    def __unicode__(self):
        return '[Xitek@%s]'%self.task_id
    
    '''
    基类成员变量说明
    self.task_type=task_type                  #任务类型
    self.task_id=task_id                      #任务ID
    self.business_id=business_id              #业务ID
    self.cur_parser_id=self.id                #当前parser ID
    self.next_parser_id=next_parser_id        #下一个parser ID
    self.url=url                              #URL地址
    self.param=self_param                     #自管理的参数信息
    self.error=[]                             #错误信息
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
            '''
          取得message的格式
          具体格式见business.business模块的businessList
            '''
            msg=self.get_message_format()
        except Exception,e:
            self.error.append('Get messge format Error:'+str(e))
            return
        
        try:
            '''对soup的解析过程'''

            table=soup.find('table',{'class':'tbc2'})

            msg['Contact']=[]
            try:
                mail_tag=table.findAll('tr')[1].findAll('td')[9]
                if not mail_tag is None and mail_tag.text>'':
                    msg['Contact'].append([u'邮件',mail_tag.text])
            except :
                pass

            try:
                tel_tag=table.findAll('tr')[2].findAll('td')[1]
                if not tel_tag is None and tel_tag.text>'':
                    msg['Contact'].append([u'电话',tel_tag.text])
            except :
                pass

            try:
                qq_tag=table.findAll('tr')[2].findAll('td')[3]
                if not qq_tag is None and qq_tag.text>'':
                    msg['Contact'].append([u'QQ/MSN',qq_tag.text])
            except :
                pass

            content_list=table.findAll('td',{'class':'tbc1 img1'})
            for content_tag in content_list:
                msg['Content']+=self.extract_text(content_tag)+'\n'



            '''
            解析完毕将msg加入队列
            state:任务状态，1已完成，0需继续处理
            id：新纪录置None或者0，老纪录置self.task_id
            '''
            message={'data':msg,'state':1,'id':self.task_id}
            self.message.append(message)
                
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
    url='http://exchange.xitek.com/showexchange.php?ex_threadid=208290'
    p=Photograph_Xitek_Detail('RandomTask',4,1,0,url,123,**{})
    r=p.run()
    print r
    print len(r['message'])
    for m in r['message']:
        print m['data']['Url']
        print m['data']['District']
        print m['data']['Content']
        print m['data']['Contact']


    
    
    