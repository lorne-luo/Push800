#-*- encoding: utf-8 -*-
'1'#version of parser file

import urllib2,urllib,os,copy,sys
import time,datetime,json,re
from core.module_manager import *
from core.spider import BaseSpider

class Parser_Template(BaseSpider):
    '''
            此Parse的解释
    '''
    
    '''返回parser的名称，尽量简短但便于识别'''
    def __unicode__(self):
        return '[%d]%s'%(self.task_id,self.__class__.__name__)
    
    '''
            基类成员变量说明
    self.task_type=task_type                                                        #任务类型
    self.task_id=task_id                                                            #任务ID
    self.business_id=business_id                                                    #业务ID
    self.cur_parser_id=self.id                                                      #当前parser ID
    self.next_parser_id=next_parser_id                                              #下一个parser ID
    self.url=url                                                                    #URL地址
    self.param=self_param                                                           #自管理的参数信息
    self.error=''                                                                   #错误信息
    self.message=[]
    
    self.get_message_format()                 #根据businessid返回message消息的空结构
    self.download_page(url)                   #下载网页,返回其htmldom
    set_encoding(encode)                      #网页的编码格式，一般中文网页设为gb18030
    '''
    def parse(self,soup):
        '''
        soup为目标网页的htmldoc
        解析htmldoc采用第三方库BeautifulSoup，使用说明参考以下网址
        http://www.crummy.com/software/BeautifulSoup/documentation.zh.html
        '''
        try:
            '''从self.param取出自管理参数'''
            #prelasttime=datetime.datetime.strptime(self.param['last_post_time'],'%Y-%m-%d %H:%M:%S')
            
            pass
        except Exception,e:
            self.error='Get self.param, Error:'+str(e)
            return
            
        try:
            #对soup的解析过程

            #取得message的格式
            #具体格式见business.business模块的businessList
            msg=self.get_message_format()
            msg['Url']=self.url

            msg['City']= ''
            msg['City_id']=0
            msg['District']= ''
            msg['District_id']=0
            msg['Title']=''
            msg['Url']=''
            msg['Price']=0
            msg['Seller']=''
            msg['Content']==''
            msg['Contact']=[]
            msg['Time']=''
            msg['Quality']=0
            msg['Pics']==[]
            
            
            #解析完毕将msg加入队列
            #state:任务状态，1已完成，0需继续处理
            #id：新纪录置None或者0，老纪录置self.task_id
            item={'data':msg,'state':1,'id':self.task_id}
            self.message.append(item)
            self.success=True
        except Exception,e:
            self.error='Parse Error:'+str(e)
            return

'''Test'''
if __name__ == '__main__':
    #load_all_module()
    
    p=Parser_Template('RandomTask',5042,1,0,'http://www.fengniao.com/secforum/',**{'post_id':1286555})
    print p.__doc__
    #r=p.run()
    #print r
    
    
    
    