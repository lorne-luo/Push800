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

class Photograph_Taobao_Detail(BaseSpider):
    '''
    此Parse的解释
    '''

    def __unicode__(self):
        return '[Taobao@%s]'%self.task_id
    
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

            item=soup.find('ul',{'class':'item-info'})
            price_tag=item.find('li',{'class':'price'})
            if not price_tag is None:
                pricestr=unistr.extract_number(price_tag.text)
                msg['Price']=int(float(pricestr))

            city_tag=item.find("li", { "class" : "orgin" })
            if not city_tag is None:
                citystr=city_tag.text[5:]
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
                if districtstr>'':
                    d=cityparser.extract_district(districtstr)
                    msg['District']=d[1]
                    msg['District_id']=d[0]

            contact_div=soup.find("div", { "id" : "contact-info" })
            if not contact_div is None:
                seller_tag=contact_div.find("span", { "class" : "tb-contact-person" })
                if not seller_tag is None:
                    msg['Seller']=seller_tag.text
                tel_tag=contact_div.find("img", { "id" : "tel-num" })
                if not tel_tag is None:
                    msg['Contact']=[]
                    msg['Contact'].append([u'电话',tel_tag['src']])

            content_tag=soup.find("div", { "id" : "item-desc" })
            content_url=content_tag['data-url']
            headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',\
                       'Referer':msg['Url'],'Content-Type': 'application/x-www-form-urlencoded'}
            req=urllib2.Request(url=content_url,headers = headers)
            page = urllib2.urlopen(req,timeout=30)
            content_str=unicode(page.read(),'GBK')
            content_str=content_str[10:]
            #print content_str
            desc = BeautifulSoup('<body>'+content_str+'</body>')
            #print str(type(desc.body))
            msg['Content']=self.extract_text(desc.body)
            #print content_str

            title_tag=soup.find("h1", { "class" : "item-title" })
            if not title_tag is None:
                msg['Title']=title_tag.text
                if msg['Title'].find(u'求购')>-1:
                    msg['Is_sell']=False

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
    url='http://ershou.taobao.com/item.htm?id=14676685858&from=list&similarUrl=http://s.ershou.taobao.com/list/json_list.htm?stype=1%26catid=50025242%26divisionId=110100%26st_edtime=1'
    p=Photograph_Taobao_Detail('RandomTask',4,1,0,url,123,**{})
    r=p.run()
    print r
    print len(r['message'])
    for m in r['message']:
        print m['data']['Url']
        print m['data']['District']
        print m['data']['Content']
        print m['data']['Contact']




def test():
        #urllib.urlretrieve(m['data']['Contact'][0][1],'1.bmp')
        req = urllib2.Request('http://ershou.taobao.com/phone_2_image.do?q_p=rO0ABXQACzE4NjE4MzgzNTI3')
        req.add_header('Referer', 'http://ershou.taobao.com/')
        r = urllib2.urlopen(req)

        tfp = open('test.jpg', 'wb')
        bs = 1024*8
        while 1:
            block = r.fp.read(bs)
            if block == "":
                break
            tfp.write(block)
        tfp.close()

    
    
    