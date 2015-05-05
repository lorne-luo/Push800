#-*- encoding: utf-8 -*-
'1'#version of parser file

import urllib2,urllib,os,copy,sys
import time,datetime,json,re

from BeautifulSoup import BeautifulSoup
from business.business import getBusinessMessageByID
from spiders.Photograph_Fengniao_All_Detail import Photograph_Fengniao_All_Detail_ByID
import utils.brand as brand

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)


def Photograph_Fengniao_All_List(task_type,task_id,business_id,cur_parser_id,next_parser_id,url,**self_param):
    '''
           蜂鸟二手摄影器材交易版list页面,不区分城市
    http://www.fengniao.com/secforum/search.php?bsid=2&stid=2&ptypeid=2&tkey=&sortorder=&daysprune=&sortfield=posttime
            
          参数解释:
    task_type          任务类型
    task_id            任务id
    business_id        业务id
    cur_parser_id      当前解析函数id
    next_parser_id     下一步解析函数id
    url                网址
    self_param         自管理参数
    '''
    #------------------------------------------------------------------------------------------
    '''返回信息结果类型'''
    result={'run_info':{},'task_info':{},'message':[]}

    result['run_info']['time_cost']=0                             #任务耗时
    result['run_info']['page_count']=0                            #访问页面数量
    result['run_info']['data_trans']=0                            #数据传数量
    
    result['task_info']['success']=False                          #任务是否成功
    result['task_info']['error']=''                               #err信息
    result['task_info']['task_type']=task_type                    #任务类型
    result['task_info']['task_id']=task_id                        #任务ID
    result['task_info']['business_id']=business_id                #业务ID
    result['task_info']['cur_parser_id']=cur_parser_id            #当前parser ID
    result['task_info']['next_parser_id']=next_parser_id          #下一个parser ID
    result['task_info']['self_param']=self_param                  #自管理的参数信息
    
    '''用来返回message'''
    result['message']=[]
    #------------------------------------------------------------------------------------------
    
    '''数据库中最后发帖时间和最后ID'''
    prelasttime=datetime.datetime.strptime(self_param['last_post_time'],'%Y-%m-%d %H:%M:%S')
    prelastid=int(self_param['last_post_id'])
    '''记录新最后发帖时间的临时变量'''
    newlasttime=prelasttime
    newlastid=prelastid

    page = urllib2.urlopen(url)
    pagedata=page.read()
    result['run_info']['page_count']+=1
    result['run_info']['data_trans']+=len(pagedata)
    soup = BeautifulSoup(pagedata,fromEncoding="gb18030")
    
    try:
        table=soup.find("table", { "class" : "mt10" })
        if table==None:
            print '    Warning:没有数据项'
            return None
        i=0
        trlist=table.findAll("tr",limit=10)
        for tr in trlist:
            if i==0:
                i=i+1
                continue
            td=tr.findAll("td")
            
            '''更新两个自管理参数'''
            '''发帖时间'''
            posttime=datetime.datetime.strptime('20'+td[9].text,'%Y-%m-%d %H:%M')
            '''帖子ID'''
            try:        
                p=re.compile(r'\/(\d+).html$')
                v = p.findall(td[2].find("a")['href'])
                postid=int(v[0])
            except:
                postid=0
            
            if posttime<=prelasttime and postid<=newlastid:
                break
            if posttime>newlasttime:
                    newlasttime=posttime
            if postid>newlastid:
                    newlastid=postid
            
            '''根据businessid获取message类'''
            try:
                m = copy.deepcopy(getBusinessMessageByID(business_id))
            except Exception,e:
                result['task_info']['error']= str(e)
                return json.dumps(result)
                
            m['Time']=posttime.strftime('%Y-%m-%d %H:%M:%S')
            m['Title']=td[2].text
            m['Brand_id']=brand.extract_brand(m['Title'])
            m['City']=td[4].text
            m['Url']=td[2].find("a")['href']
            m['Quality']=td[5].text
            m['Quality']=m['Quality'][:len(m['Quality'])-1]
            m['Price']=td[6].text[1:]
            m['District']=td[4].text
            
            paramstr=''
            if type(posttime) is datetime.datetime:
                paramstr+="post_time='"+posttime.strftime('%Y-%m-%d %H:%M:%S')+"'"
            if paramstr!='' and postid>0:
                paramstr+=",post_id="+str(postid)
            else:
                paramstr+="post_id="+str(postid)
                
            item={'data':m,'param':paramstr,'state':0}
            
            result['message'].append(item)
    except Exception,e:
        result['task_info']['error']='Check tr Error:'+str(e)
        return result
    
    
    '''list页面没有更新，沿ID爬行'''
    if len(result['message'])==0:
        #下一个id str(prelastid+1) todo 改成循环
        result['task_info']['next_parser_id']=3#和业务相关了3是Photograph_Fengniao_All_Detail_ByID
        nextm={}
        for offset in range(20):
            idnow=prelastid+offset+1
            try:
                nextm=Photograph_Fengniao_All_Detail_ByID('RandomTask',0,1,3,0,'http://www.fengniao.com/secforum/',**{'post_id':idnow})
                result['run_info']['page_count']+=nextm['run_info']['page_count']
                result['run_info']['data_trans']+=nextm['run_info']['data_trans']
                
                if nextm['task_info']['success']:
                    result['message']+=nextm['message']
                    if newlasttime < datetime.datetime.strptime(nextm['task_info']['self_param']['post_time'],'%Y-%m-%d %H:%M:%S'):
                        newlasttime=datetime.datetime.strptime(nextm['task_info']['self_param']['post_time'],'%Y-%m-%d %H:%M:%S')
                        
                    if idnow>newlastid:
                        newlastid=idnow
                    
                    print '---NextID='+str(idnow)+' Success'
                else:
                    if nextm['task_info']['error']=='NULL_PAGE':
                        print '---NextID='+str(idnow)+' NULL_PAGE'
                        break
                    elif nextm['task_info']['error']=='MERCHANT_PAGE':
                        if idnow>newlastid:
                            newlastid=idnow
                        print '---NextID='+str(idnow)+' MERCHANT_PAGE'
                        continue
                    else:
                        print '---NextID='+str(idnow)+' '+nextm['task_info']['error']
                        continue
            except Exception,e:
                print '---NextID='+str(idnow)+' ErrinList:'+str(e)
                continue
        result['message'].reverse()
        
    '''最后发帖时间'''   
    if not (newlasttime==prelasttime and newlastid==prelastid): 
        self_param['last_post_id']=newlastid
        self_param['last_post_time']=newlasttime.strftime('%Y-%m-%d %H:%M:%S')
    
    '''有新的帖子才更新参数'''
    if len(result['message'])>0:
        result['message'].reverse()
    result['task_info']['self_param']=self_param    
    result['task_info']['success']=True
        
    #data = {'result':json.dumps(result, ensure_ascii=False)}
    #echo = post(TASKSUBMITURL, data)
    #print '    Submited List='+echo
    #print json.dumps(ret)
    return result

'''Test'''
if __name__ == '__main__':
    print Photograph_Fengniao_All_List('FixTask',1,1,1,2,'http://www.fengniao.com/secforum/search.php?bsid=2&stid=2&ptypeid=2&tkey=&sortorder=&daysprune=&sortfield=posttime',**{'last_post_id':1284116,'last_post_time':'2011-11-09 15:16:00'})
    #print Photograph_Fengniao_All_List('FixTask',1,1,0,2,'http://www.fengniao.com/secforum/search.php?bsid=2&stid=2&ptypeid=2&tkey=&sortorder=&daysprune=&sortfield=posttime','2011-10-21 14:22:00','1265679','')
    #m =getBusinessMessageByID(1)
    
    
    