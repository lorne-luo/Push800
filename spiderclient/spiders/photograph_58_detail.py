#-*- encoding: utf-8 -*-
'1'#version of parser file

import urllib2,urllib,os,copy,sys,traceback
import time,datetime,json,re
import utils.city as cityparser
from utils.BeautifulSoup import NavigableString, Tag
import utils.brand as brand
from core.module_manager import *
from core.spider import BaseSpider

class Photograph_58_Detail(BaseSpider):
    '''
    此Parse的解释
    '''

    def __unicode__(self):
        return '[58@%s]'%self.task_id
    
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
            parainfo=soup.find('p',{'class':'parainfo'})
            if parainfo==None:
                self.error='NULL PAGE'
                return

            msg['Url']=self.url
            price_str=parainfo.find('em',{'class':'b'})
            if price_str.text.isdigit():
                msg['Price']=int(price_str.text)
            else:
                #0代表面议
                msg['Price']=0

            quality_str=parainfo.find('i',{'class':'cs'})
            if quality_str is None:
                msg['Quality']=0
                if soup.find('h1').text.find(u'求购'):
                    msg['Is_sell']=False
            else:
                quality_str=quality_str.text
                if quality_str=='全新':
                    msg['Quality']=100
                elif quality_str.endswith(u'成新'):
                    quality_str=quality_str[:len(quality_str)-2]
                    if quality_str.isdigit() and len(quality_str)==1:
                        msg['Quality']=int(quality_str+'0')
                    elif quality_str.isdigit() and len(quality_str)==2:
                        msg['Quality']=int(quality_str)

            city_str=parainfo.findAll('i',{'class':'r'})[1].findNextSibling()
            c=cityparser.extract_city(city_str.text)
            if c[0]==0:
                msg['District']=city_str.text

            newuser_tag=soup.find('div',{'id':'newuser'}).findNextSibling()
            i= newuser_tag.text.find('username:')
            j=newuser_tag.text.find('\',',i)
            msg['Seller']=newuser_tag.text[i+10:j]

            msg['Contact']=[]
            contactlist=soup.find('ul',{'class':'contactlist hideclasses'})
            if not contactlist is None:
                tels=contactlist.findAll('li')
                if not tels is None:
                    for t in tels:
                        if t.text.startswith('联系电话'):
                            img=t.find('img')
                            if img is None:
                                c=str(t.find('span',{'class':'tel'}).contents)
                                m = re.search('(?<=\')http://image.58.com.*(?=\')', t.find('span',{'class':'tel'}).text)
                                tel_pic=m.group(0)
                                msg['Contact'].append([u'电话',tel_pic])
                            else:
                                msg['Contact'].append([u'电话',img['src']])
                        elif t.text.startswith('QQ'):
                            img=t.find('img')
                            if img is None:
                                m = re.search('(?<=\')http://image.58.com.*(?=\')', str(t.contents))
                                qq_pic=m.group(0)
                                msg['Contact'].append([u'QQ/MSN',qq_pic])
                            else:
                                msg['Contact'].append([u'QQ/MSN',img['src']])

            content_tag=soup.find('div',{'class':'maincon'})
            msg['Content']=self.extract_text(content_tag)

            #msg['Brand_id']=brand.extract_brand(msg['Content'])

            msg['Pics']=[]
            img_view=soup.find('ul',{'class':'img_view'})
            if not img_view is None:
                pics=img_view.findAll('img')
                for p in pics:
                    msg['Pics'].append(p['src'])


            '''
            解析完毕将msg加入队列
            state:任务状态，1已完成，0需继续处理
            id：新纪录置None或者0，老纪录置self.task_id
            '''
            item={'data':msg,'state':1,'id':self.task_id}
            self.message.append(item)
                
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
    
    p=Photograph_58_Detail('RandomTask',4,1,0,'http://bj.58.com/shuma/9774866428682x.shtml',123,**{})
    r=p.run()
    print r
    print len(r['message'])
    for m in r['message']:
        print m['data']['District']
        print m['data']['Content']
        print m['data']['Contact']

    
    
    