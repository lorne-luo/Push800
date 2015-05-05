#-*- encoding: utf-8 -*-
'1'#version of parser file

import urllib2,urllib,os,copy,sys
import time,datetime,json,re,traceback
from utils.BeautifulSoup import NavigableString, Tag
import utils.city as cityparser
from core.module_manager import *
from core.spider import BaseSpider

class Photograph_Ganji_Detail(BaseSpider):
    '''
            此Parse的解释
    '''

    def __unicode__(self):
        return '[Ganji@%s]'%self.task_id

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
            '''对soup的解析过程'''
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

            #时间和价格
            ptags=soup.findAll('p',{'class':'mt'})
            if len(ptags)==0:
                if len(soup.findAll('div',{'class':'cont_error_img'}))>0:
                    self.error='NULL PAGE'
                    return
            p1str=ptags[0].text

            fr=soup.find('span',{'class':'fr'})
            timestr=fr.nextSibling
            timestr=timestr[timestr.find('发布时间：')+5:]
            timestr=str(datetime.datetime.now().year)+'-'+timestr+':00'
            msg['Time']=timestr

            price_tag=ptags[0].find('span',{'class':'ft-red'})
            pricestr=price_tag.text
            msg['Price']=pricestr

            sellerstr=ptags[0].find('br').nextSibling
            sellerstr=sellerstr[sellerstr.find('联系人：')+4:]
            sellerstr=sellerstr.replace(u'\t','').replace(u'\n','').replace(u' ','')
            msg['Seller']=sellerstr

            msg['Contact']=[]
            contact_tag=ptags[0].findAll('img',{'align':'absmiddle'})
            contact_count=len(contact_tag)
            for i in range(contact_count):
                name=contact_tag[i].previousSibling.replace(u'\t','').replace(u'\n','').replace(u' ','')
                url='http://www.ganji.com'+contact_tag[i]['src']
                name=name.strip()
                msg['Contact'].append((name[:len(name)-1],url))

            msg['Pics']=[]
            piclist_tag=soup.find('p',{'class':'xiangguancaozuo mt'}).findNextSibling()
            piclist=piclist_tag.findAll('img')

            for img in piclist:
                if img.findParent().name=='a':
                    msg['Pics'].append(img['src'])

            #msg['District']=p1str[p1str.find('所在地：')+4:]
            temp_a=price_tag
            for i in range(4):
                temp_a=temp_a.findNextSibling()
                if temp_a.name=='a':
                    d=cityparser.extract_district(temp_a.text)
                    if len(d)>1 and d[0]>0 :
                        msg['District']=d[1]
                        msg['District_id']=d[0]
                        break

            msg['Content']=self.extract_text(ptags[1])

            msg['Url']=self.url
            #state=0 if content.endswith('…') else 1
            '''
            解析完毕将msg加入队列
            state:任务状态，1已完成，0需继续处理
            id：新纪录置None或者0，老纪录置self.task_id
            '''
            item={'data':msg,'state':1,'id':self.task_id}
            self.message.append(item)

            '''更新自管理参数'''
            if len(self.message)>0:
                self.param['last_post_time']=self.message[0]['data']['Time']
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
    #http://bj.ganji.com/shuma/11112223_8554968.htm
    #http://bj.ganji.com/shuma/11112301_8555234.htm
    p=Photograph_Ganji_Detail('RandomTask',45087,1,0,'http://tj.ganji.com/shuma/243750147x.htm',1,\
                              **{})
    r=p.run()
    print r
    #print len(r['message'])
    #print r['message'][0]['data']['Contact']
    #print r['message'][0]['data']['Seller']
    r['task_info']['cur_parser_id']=7
    data = {'submit':r['task_info']['task_type'],'result':json.dumps(r, ensure_ascii=False)}
    #echo = post(setting.SUBMIT_TASK_URL, data)
    #print echo
    for m in r['message']:
        print m['data']['District']
        print m['data']['Content']
    
    