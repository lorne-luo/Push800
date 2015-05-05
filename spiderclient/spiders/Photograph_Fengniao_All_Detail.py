#-*- encoding: utf-8 -*-
'1'#version of parser file

import urllib2,urllib,os,time,copy,json,re,datetime,sys
from BeautifulSoup import BeautifulSoup
from business.business import getBusinessMessageByID
from utils.log import *
import utils.brand as brand

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)


def Photograph_Fengniao_All_Detail(task_type,task_id,business_id,cur_parser_id,next_parser_id,url,**self_param):
    '''
           蜂鸟二手摄影器材detail页面,不区分城市
           例：http://www.fengniao.com/secforum/1242131.html
           
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
    #result['message'][0]['data']=                                #消息的实体数据
    #result['message'][0][state'']=                               #任务状态0未完成，1完成
    #result['message'][0]['id']=                                  #任务ID
    
    #------------------------------------------------------------------------------------------
    Parse(url,result,**self_param)
        
    #data = {'result':json.dumps(r)}
    #echo=post(TASKSUBMITURL, data)
    #print '    Submited Detail:'+echo
    return result

def Photograph_Fengniao_All_Detail_ByID(task_type,task_id,business_id,cur_parser_id,next_parser_id,url,**self_param):
    '''
           蜂鸟二手摄影器材detail页面,不区分城市
           例：http://www.fengniao.com/secforum/1242131.html
           
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
    #result['message'][0]['data']=                                #消息的实体数据
    #result['message'][0][state'']=                               #任务状态0未完成，1完成
    #result['message'][0]['id']=                                  #任务ID
    
    #------------------------------------------------------------------------------------------
    
    url+=str(self_param['post_id'])+'.html'
    Parse(url,result,**self_param)
    
    #data = {'result':json.dumps(r, ensure_ascii=False)}
    #echo=post(TASKSUBMITURL, data)
    #print '    Submited Detail:'+echo
    return result

def Parse(url,result,**self_param):
    
    postid=0
    '''取post_id'''
    if self_param.has_key('post_id'):
        postid=int(self_param['post_id'])
    else:
        p=re.compile(r'\/(\d+).html$')
        v = p.findall(url)
        if len(v)>0:
            try:
                postid=int(v[0])
            except:
                pass    
            
    '''根据businessid获取message类'''
    try:
        m =copy.deepcopy(getBusinessMessageByID(result['task_info']['business_id']))
    except Exception,e:
        result['task_info']['error']= str(e)
        return (result)
        
    m['Url']=url
    page = urllib2.urlopen(url)
    pagedata=page.read()
    result['run_info']['page_count']+=1
    result['run_info']['data_trans']+=len(pagedata)
    soup = BeautifulSoup(pagedata,fromEncoding="gb18030")
    if len(str(soup))<120:
        result['task_info']['error']='NULL_PAGE'
        return result
   
    try:
        table=soup.find("table", { "border" : "1" })
        #print table
        hr=table.find("hr", { "align" : "left" })
        if hr!=None:
            for t in hr.findNextSiblings():
                t.extract()
        else:
            result['task_info']['error']='MERCHANT_PAGE'
            return result
        #这里要做异常验证
        m['Contact']=table.findAll("tr")[1].findAll("td")[3].text
        m['Price']=table.findAll("tr")[0].findAll("td")[1].text[1:]
        m['City']=table.findAll("tr")[1].findAll("td")[1].text
        timestr=soup.find("font", { "color" : "#006666" }).findParent().text
        posttime=datetime.datetime.strptime(timestr,'%m-%d-%Y%H:%M')
        m['Time']=posttime.strftime('%Y-%m-%d %H:%M:%S')
        title=soup.find("h1", { "class" : "h1" }).text
        #!!这里用正则
        index=title.index('新')
        m['Quality']=title[:index]
        m['Title']=title[index+2:]
        m['Brand_id']=brand.extract_brand(m['Title'])
        m['Seller']=soup.findAll("table", { "cellpadding" : "4" })[1].find("font").text
        
        content_td=table.find("td", { "colspan" : "4" })
        #print '    ',len('"进行交易。 您也可以选择通过""交易为了交易安全，交易前请查看""、""')=95=37
        content=content_td.text
        content=content[0:len(content)-37]
        m['Content']=content
        
        result['task_info']['self_param']['post_time']=posttime.strftime('%Y-%m-%d %H:%M:%S')
        result['task_info']['self_param']['post_id']=postid
            
        item={'data':m,'state':1,'id':result['task_info']['task_id']}
        result['message'].append(item)
        
        result['task_info']['success']=True
    except Exception,e:
        result['task_info']['error']=str(e)
        result['task_info']['success']=False
        print e
    return result

'''Test'''
if __name__ == '__main__':
    #参数固定版
    #print Photograph_Fengniao_All_Detail('RandomTask',1,1,2,0,'http://www.fengniao.com/secforum/1259815.html','','','')
    #print Photograph_Fengniao_All_Detail_ByID('RandomTask',0,1,3,0,'http://www.fengniao.com/secforum/','1266641','','')
    
    #字典参数版
    print Photograph_Fengniao_All_Detail('RandomTask',5042,1,2,0,'http://www.fengniao.com/secforum/1278402.html',**{})
    #print Photograph_Fengniao_All_Detail_ByID('RandomTask',4610,1,2,0,'http://www.fengniao.com/secforum/',**{'post_id':1277734})
    
    
    