#-*- encoding: utf-8 -*-
#version
'1'

import urllib2,time,copy,sys,threading,traceback,os,datetime
from utils.log import *
from utils.BeautifulSoup import BeautifulSoup
from utils.BeautifulSoup import NavigableString, Tag
from business.business import getBusinessMessageByID
import setting

#各线程间共用的独占锁
spiderlock = threading.RLock()

class BaseSpider(object):
    '''
    spider父类
    '''

    def __init__(self,task_type,task_id,business_id,next_parser_id,url,token,**self_param):
        '''
        Constructor
        '''
        #访问页面数量  数据传数量  下载耗时  解析耗时  
        self.profiler={'page_count':0,'data_trans':0,'download_duration':0,'parse_duration':0}
        self.encoding='gb18030'    #编码格式
        self.success=False         #任务是否成功
        self.phone_user_agent=False#是否使用手机浏览器的user_agent去爬行，省流量
        
        self.task_type=task_type                                                        #任务类型
        self.task_id=task_id                                                            #任务ID
        self.business_id=business_id                                                    #业务ID
        self.cur_parser_id=self.__class__.id if hasattr(self.__class__,'id') else 0                         #当前parser ID
        self.next_parser_id=next_parser_id                                              #下一个parser ID
        self.url=url                                                                    #URL地址
        self.param=self_param                                                           #自管理的参数信息
        self.error=[]                                                                   #错误信息
        self.message=[]
        self.assign_token=token
        
    def set_encoding(self,encoding):
        '''网页的编码格式，一般中文网页设为gb18030'''
        self.encoding=encoding
        
    def get_message_format(self):
        '''根据businessid返回message消息的空结构'''
        return copy.deepcopy(getBusinessMessageByID(self.business_id))
        
    def download_page(self,url):
        '''下载网页,返回其htmldom'''
        #'HTTP_USER_AGENT': 'JUC (Linux; U; 2.2.1; zh-cn; Milestone_XT720; 480*854) UCWEB7.9.3.103/139/800'
        try:
            if self.phone_user_agent:
                headers = {'User-Agent':'JUC (Linux; U; 2.2.1; zh-cn; Milestone_XT720; 480*854) UCWEB7.9.3.103/139/800'}
            else:
                headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
                
            req=urllib2.Request(url=url,headers = headers)
            page = urllib2.urlopen(req)
            data=page.read()
            self.profiler['page_count']+=1
            self.profiler['data_trans']+=len(data)
            soup = BeautifulSoup(data,fromEncoding=self.encoding)
            return soup
        except Exception,e:
            raise e
    
    def parse(self,soup):
        '''
                    解析网页
        '''
        try:
            
            
            
            pass
        except Exception,e:
            self.error.append('[%s]%s parse error:%s'%(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),self.__class__.__name__,str(e)))
            info = sys.exc_info()
            print "Parser Error:%s: %s" % info[:2]
            for file, lineno, function, text in traceback.extract_tb(info[2]):
                s='*%s,line %s,%s()'%(os.path.split(file)[1],lineno,function)
                self.error.append(s)
                print s

    def encode_html(self,s):
        if type(s) is str or type(s) is unicode:
            s=s.replace('&nbsp;',u' ')
            s=s.replace('\t','')
            s=s.replace('\n','')
            s=s.replace('\r','')
            s=s.replace('&lt;',u'<')
            s=s.replace('&gt;',u'>')
            s=s.replace('&amp;',u'&')
            s=s.replace('&yen;',u'￥')
            s=s.replace('&cent;',u'￠')
            s=s.replace('&pound;',u'￡')
            s=s.replace('&euro;',u'€')
            s=s.replace('&sect;',u'§')
            s=s.replace('&copy;',u'?')
            s=s.replace('&reg;',u'?')
            s=s.replace('&trade;',u'?')
            s=s.replace('<br>',u'\n')
            s=s.replace('<br/>',u'\n')
            s=s.replace('<br />',u'\n')
        return  s.strip()

    def get_result(self):
        '''
                    组装任务结果
        '''
        result={'spider_info':{},'run_info':{},'task_info':{},'message':[]}
    
        result['spider_info']['token']=setting.TOKEN
        
        result['run_info']['page_count']=self.profiler['page_count']                    #任务耗时
        result['run_info']['data_trans']=self.profiler['data_trans']                    #访问页面数量
        result['run_info']['download_duration']=self.profiler['download_duration']      #数据传数量
        result['run_info']['parse_duration']=self.profiler['parse_duration']            #数据传数量
        
        result['task_info']['success']=self.success                        #任务是否成功
        result['task_info']['error']=self.error                            #err信息
        result['task_info']['task_type']=self.task_type                    #任务类型
        result['task_info']['task_id']=self.task_id                        #任务ID
        result['task_info']['business_id']=self.business_id                #业务ID
        result['task_info']['cur_parser_id']=self.cur_parser_id            #当前parser ID
        result['task_info']['next_parser_id']=self.next_parser_id          #下一个parser ID
        result['task_info']['self_param']=self.param                       #自管理的参数信息
        result['task_info']['assign_token']=self.assign_token                     #任务token


        '''用来返回message'''
        result['message']=self.message
        return result
    
    def run(self):
        '''
        Spider开始执行的函数
        '''
        #出现错误'ascii' codec can't decode byte 0xe9 in position 0: ordinal not in range(128)" 的解决方法 .
        default_encoding = 'utf-8'
        if sys.getdefaultencoding() != default_encoding:
            reload(sys)
            sys.setdefaultencoding(default_encoding)
        
        retry=0
        soup=None
        
        #下载页面
        starttime=time.time()
        try:
            soup = self.download_page(self.url)
        except Exception,e:
            if retry<3:
                msg="[%s.%s %d] %s : %s"%(self.__class__.__name__, 'download_page',\
                        sys._getframe().f_lineno,type(e).__name__,str(e))
                info(msg)
                retry+=1
            else:
                msg="[%s.%s %d] %s : %s"%(self.__class__.__name__, 'download_page',\
                        sys._getframe().f_lineno,type(e).__name__,'download_page error retry 3 times')
                err(msg)
                self.error.append(msg)
                self.profiler['download_duration']=time.time()-starttime
                return self.get_result()
            
        self.profiler['download_duration']=time.time()-starttime
        
        #解析页面
        starttime=time.time()
        try:
            if soup==None:
                raise Exception('Soup is None')
            self.parse(soup)
        except Exception,e:
            err(str(e))
            self.error.append(str(e))
        self.profiler['parse_duration']=time.time()-starttime

        return self.get_result()
        
    def __unicode__(self):
        return "<%s at 0x%0x>" % (type(self).__name__, id(self))
    
    def extract_text(self,tag):
        res=u''
        if type(tag) is Tag:
            for s in tag.contents:
                if type(s) is Tag:
                    if s.name=='br':
                        res+=u'\n'
                    elif s.name=='hr':
                        break
                    else:
                        res+=self.extract_text(s)
                elif type(s) is NavigableString:
                    #res+=unicode(s).replace('&nbsp;',' ').replace('\n','').replace('\n','').replace('\r','').replace('\t','').strip()
                    res+=self.encode_html(unicode(s))
        elif type(tag) is NavigableString:
            res+=self.encode_html(unicode(s))
            #res+=unicode(s).replace('\n','').replace('\r','').replace('\t','').strip()
        return res

    