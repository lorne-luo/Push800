#-*- encoding: utf-8 -*-
'''
存储所有与爬虫服务器相关的持久化信息，
考虑这部分信息量较少且相对比较稳定，
直接使用内存存储这部分数据，

业务列表的属性：
1.id
2.名称
3.message的格式（提交给服务器）
SpiderParse中通过getBusinessNameByID(businessid)函数来取得message

Created on 2011-9-21

@author: Leo
'''
from ctypes import *
import sys,imp

class SpiderBusiness(Structure):
    '''
            爬行的商品种类
    '''
    id=0
    name=''
    message={}

    def __init__(self,id,name,messagetype):
        self.id=id
        self.name=name
        self.message=messagetype


businessList=[]
businessList.append(SpiderBusiness(1,'Photograph',\
            {'City': '','City_id':0, 'District': '','District_id':0, 'Title': '', 'Url': '', 'Price': 0, 'Brand_id':0,'Seller': '', 'Is_sell': True, 'Content': '', 'Contact': [], 'Time': '', 'Quality': 0,'Pics':[]}))
businessList.append(SpiderBusiness(2,'Mobile',\
            {'City': '', 'District': '', 'Title': '', 'Url': '', 'Price': '', 'Seller': '', 'Content': '', 'Contact': '', 'Time': '', 'Quality': ''}))

#通过name获取businessid
def getBusinessIDByName(name):
    for b in businessList:
        if b.name.lower()==name.lower():
            return b.id
            break
    return 0

def getBusinessNameByID(id):
    for b in businessList:
        if b.id==id:
            return b.name
            break
    return None

def getBusinessMessageByID(id):
    for b in businessList:
        if b.id==id:
            
            return b.message
            break
    return None

'''Test'''
if __name__ == '__main__':
    print getBusinessMessageByID(1)
#try:
#    a =getBusinessMessageByID(1)
#    print a.__dict__
#except Exception,e:
#    print e



#print imp.find_module('message')
#fp, pathname, description = imp.find_module('message')
#stringmodule = imp.load_module('message',*imp.find_module('SpiderBusiness'))
#messagemodule = imp.load_module('',*imp.find_module('message'))
#print dir (stringmodule)

#from SpiderTask.spidertask import *
#load_module('*','message','SpiderBusiness')
#for b in businessList:
#    print b.id,b.name,b.spiderTask,b.messageType
#b = Business(1, 'sdgdsg', 'sdgdsg')
#print b.id, b.name,b.spidertype,b.messagetype   

 