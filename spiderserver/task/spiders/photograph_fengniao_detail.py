#-*- encoding: utf-8 -*-
'1'#version of parser file

import urllib2,urllib,os,copy,sys,traceback
import time,datetime,re,json
import utils.city as cityparser
from core.spider import BaseSpider
import utils.brand as brand

class Photograph_Fengniao_Detail(BaseSpider):
    '''
    蜂鸟二手摄影器材detail页面
    例：http://www.fengniao.com/secforum/1242131.html
    '''
    
    def __unicode__(self):
        return '[Fengniao@%s]'%self.task_id

    def parse(self,soup):
        try:
            postid=0
            '''取post_id'''
            if self.param.has_key('post_id'):
                postid=int(self.param['post_id'])
            else:
                p=re.compile(r'\/(\d+).html$')
                v = p.findall(self.url)
                if len(v)>0:
                    try:
                        postid=int(v[0])
                    except:
                        pass
            
            m=self.get_message_format()
            m['Url']=self.url
            
            #判断是否是空页面
            if len(str(soup))<120:
                self.error.append('NULL_PAGE')
                return
       
        
            table=soup.find("table", { "border" : "1" })
            #print table
            hr=table.find("hr", { "align" : "left" })
            if hr!=None:
                for t in hr.findNextSiblings():
                    t.extract()
            else:
                #是商家页面
                self.error.append('MERCHANT_PAGE')
                return
            #这里要做异常验证
            m['Contact']=table.findAll("tr")[1].findAll("td")[3].text
            m['Price']=table.findAll("tr")[0].findAll("td")[1].text[1:]

            c=cityparser.extract_city(table.findAll("tr")[1].findAll("td")[1].text)
            m['City']=c[1]
            m['City_id']=c[0]

            d=cityparser.extract_district(table.findAll("tr")[1].findAll("td")[1].text)
            m['District']=d[1]
            m['District_id']=d[0]

            timestr=soup.find("font", { "color" : "#006666" }).findParent().text
            posttime=datetime.datetime.strptime(timestr,'%m-%d-%Y%H:%M')
            m['Time']=posttime.strftime('%Y-%m-%d %H:%M:%S')
            title=soup.find("h1", { "class" : "h1" }).text
            #!!这里最好用正则
            index=title.index('新')
            m['Quality']=title[:index]
            m['Title']=title[index+2:]
            m['Brand_id']=brand.extract_brand(m['Title'])
            m['Title']=m['Title'][m['Title'].find(' ')+1:]

            m['Seller']=soup.findAll("table", { "cellpadding" : "4" })[1].find("font").text
            
            content_td=table.find("td", { "colspan" : "4" })
            #print '    ',len('"进行交易。 您也可以选择通过""交易为了交易安全，交易前请查看""、""')=95=37
            m['Content']=self.extract_text(content_td)

            pic_table=soup.find("table", { "width" : "600" })
            if pic_table!=None:
                img_list=pic_table.findAll('img')
                #print 'pic_table',len(img_list)
                for img in img_list:
                    m['Pics'].append(img['src'])

            self.param['post_time']=posttime.strftime('%Y-%m-%d %H:%M:%S')
            self.param['post_id']=postid
                
            item={'data':m,'state':1,'id':self.task_id}
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
    t=('photograph_fengniao_detail','Photograph_Fengniao_Detail',"'RandomTask',5042,1,0,\
                        'http://www.fengniao.com/secforum/1467446.html',123,**{}")
       
    #exec('from spiders.'+t[0]+' import '+t[1])
    exec(t[1]+'.id=1')
    p=eval(t[1]+'('+t[2]+')')
    r=p.run()
    print r
    for m in r['message']:
        print m['data']['District']
        print m['data']['Content']
    
    
    
    