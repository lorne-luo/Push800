#-*- encoding: utf-8 -*-
'1'#version of parser file

import urllib2,urllib,os,copy,sys
import time,datetime,json,re
from photograph_fengniao_detail import Photograph_Fengniao_Detail
from core.module_manager import *
from core.spider import BaseSpider




class Photograph_Fengniao_Detail_ByID(Photograph_Fengniao_Detail):
    
    def __init__(self,task_type,task_id,business_id,next_parser_id,url,token,**self_param):
        '''
        Constructor
        '''
        super(Photograph_Fengniao_Detail_ByID,self).__init__(task_type,task_id,business_id,next_parser_id,url,token,**self_param)
        #Photograph_Fengniao_Detail.__init__(self,task_type,task_id,business_id,next_parser_id,url,**self_param)
        
        #Photograph_Fengniao_Detail=get_spider_byname('Photograph_Fengniao_Detail')
        #setattr(self,'parse',getattr(Photograph_Fengniao_Detail,'parse'))
        
        if self_param.has_key('post_id'):
            self.url+=str(self_param['post_id'])+'.html'

    
'''Test'''
if __name__ == '__main__':
    load_all_module()
    
    c=get_spider_byname('Photograph_Fengniao_Detail_ByID')
    p=c('RandomTask',5042,1,0,'http://www.fengniao.com/secforum/',**{'post_id':1286555})
    print p.id
    #r=p.run()
    #print r
    
    
    
    