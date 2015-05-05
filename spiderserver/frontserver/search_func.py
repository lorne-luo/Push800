#-*- encoding: utf-8 -*-
'''
所有与搜索相关的功能函数

私有函数包括分词，建倒排索引等

共有函数包括：
1.根据用户提交的keyword查询与之匹配的msg
2.根据一条msg查询与之匹配的subscribe
3.根据一条msg判断它是否是spam
其中2,3都在message_view.add_message()中调用，即新到达一条msg时调用
'''
__author__ = 'Leo'

import os
import random,sys
import re
from django.http import HttpResponse
from django.shortcuts import render_to_response
import time
from django.template.loader import get_template
from models import *
import datetime,json
from sae.mail import EmailMessage
from django.template import Template, Context
from django.core import serializers
from django.db.models import Q
import segment
from spiderserver.utils.mail import send_mutil_email,send_single_email
import base64

#cut = segment.StringCutter(None)
cut = segment.get_cutter(os.path.dirname(os.path.abspath(__file__)) + '/frq.db')
threshold = 1

class Segment(object):
    def __init__(self):
        pass
    def get_key_list(self, content):
        return None

class SplitByBlank(Segment):
    def __init__(self):
        pass
    def get_key_list(self, content):
        return content.split()

class SplitByWordCut(Segment):
    def __init__(self):
        pass

    def get_key_list(self, content):
        key_list = []
        tmp_list = content.split()
        for item in tmp_list:
            if self.is_chinese(item):
                chi_list = list(cut.parse(item.decode('utf-8')))
                key_list.extend(chi_list)
            else:
                key_list.append(item)
        return key_list

    def is_chinese(self, content):
        pattern = re.compile('[^\u4E00-\u9FA5]')
        match = pattern.match(content)
        if match:
            return True
        return False

def segment(content):
    '''
    对中文语句进行分词

    param：
        content欲进行分词的语句，str型

    return：
        由分词结果组成的list
    '''
    str_list = list(cut.parse(content.decode('utf-8')))
    return str_list

def inverted_index(msg):
    '''
    对消息model进行倒排索引，索引结果写入数据库xx表xx字段

    param：
        msg欲进行倒排索引的消息，models.Photograph_Message型

    return：
        void
    '''
    pass

def search_message(city_id,brand_id,min_price,max_price,quality,keyword):
    '''
    根据用户提交的关键字查询与之匹配的msg
    param：
        city_id                 城市id,0表示不限
        brand_id                品牌id,0表示不限
        min_price，max_price    价格范围
        quality                 成色，0表示不限
        keyword                 关键字

    return：
        符合要求的Photograph_Message的id，list型
    '''
    split = SplitByWordCut()
    key_list = split.get_key_list(keyword)
    brand = 0           #brand_id

    if brand_id == 0:       #can not get default from request
        brand = get_brand_id(key_list)      #get brand_id according keywords list
    else:
        brand = brand_id        #use default value from request

    result_list = []        #value returned
    item_list = []      #result from db
    # 查询一个月以内的记录 Entry.objects.exclude(pub_date__gt=datetime.date(2005, 1, 3)).exclude(headline='Hello')
    # 查询20天以内的
    search_day=datetime.datetime.now()-datetime.timedelta(seconds=1728000)
    if min_price >= max_price:      #have not limit of price
        if brand == 0:
            item_list = Photograph_Message.objects.filter(city_id=city_id, quality__gte=quality,\
                    publish_time__gt=search_day)\
                    .order_by('-id')[0:600]
        else:
            item_list = Photograph_Message.objects.filter(city_id=city_id, quality__gte=quality, brand_id=brand,\
                            publish_time__gt=search_day\
                            ).order_by('-id')[0:600]
    else:
        if brand == 0:
            item_list = Photograph_Message.objects.filter(city_id=city_id,
                        price__range=(min_price, max_price), quality__gte=quality,\
                        publish_time__gt=search_day)\
                        .order_by('-id')[0:600]
        else:
            item_list = Photograph_Message.objects.filter(city_id=city_id,
                            price__range=(min_price, max_price), quality__gte=quality, brand_id=brand,\
                            publish_time__gt=search_day)\
                            .order_by('-id')[0:600]
    #print 'type(item_list) = '+str(type(item_list))
    if len(key_list)==0:
        return item_list

    for i in item_list:
    #length = len(item_list)
    #while length > 0:
        #length -= 1
        estimate_title = get_estimate(key_list, i.title.encode('utf-8'))
        if estimate_title >= threshold:         #match title only
            result_list.append(i)
#        else:
#            estimate_content = get_estimate(key_list, item.content.encode('utf-8'))
#            if estimate_content >= threshold:
#                result_list.append(item)

    return result_list

def search_subscribe(msg):
    '''
    根据消息，查询与之匹配的订阅

    param：
        msg                     models.Photograph_Message型

    return：
        符合要求的models.Photograph_Subscribe的id列表，list型
    '''
    item_list = Photograph_Subscribe.objects.filter(city_id=msg.city_id)

    split = SplitByWordCut()
    result_list = []

    for item in item_list:
        key_list = split.get_key_list(item.keyword)
        estimate_title = get_estimate(key_list, msg.title.encode('utf-8'))      #match title only
        if estimate_title >= threshold:
            result_list.append(item)
#        else:
#            estimate_content = get_estimate(key_list, msg.content.encode('utf-8'))
#            if estimate_content >= threshold:
#                result_list.append(item)

    if len(result_list) > 0:        #delete Photograph_Subscribe_Message with same message_id
        Photograph_Subscribe_Message.objects.filter(message_id=msg.id).delete()

    for result in result_list:
        r = Photograph_Subscribe_Message(user_id=result.user_id, subscribe_id=result.id, message_id=msg.id)
        r.save()

	return result_list

def spam_check(msg):
    '''
    判定消息是否是spam，朴素贝叶斯方法，已有先验数据集，可推迟实现

    param：
        msg                     models.Photograph_Message型

    return：
        True or False,是否是spam
    '''
    pass

def filter_num(str_list):
    pattern = re.compile('[0-9]+|[a-z]+|[A-Z]+')
    key_list = []
    for str in str_list:
        match = pattern.match(str)
        if match:
            key_list.append(str)
    return key_list

def get_estimate(key_list, message):
    length = len(key_list)
    message=message.lower()
    count = 0
    if int(length) == 0:        #justify whether key_list is empty
        return 0

    for key in key_list:
        key=key.lower()
        index = message.find(key.encode('utf-8'))
        if int(index) > -1:
            count += 1
    return float(count)/length

def get_brand_id(key_list):
    brand = 0
    for item in key_list:
        result_list = Photograph_Brand.objects.filter(Q(name_cn=item) | Q(name_en__icontains=item) | Q(name_py__icontains=item))
        if len(result_list) > 0:
            brand = result_list[0].id
            key_list.remove(item)
            break
    return brand

def search_subscribe(msg):
    is_send=False
    if msg.brand_id==1 and msg.city_id==1:
        title=unicode(msg.title)
        content=unicode(msg.content)
#        if title.find(u'秒')>-1 or content.find(u'秒')>-1:
#            is_send=True
#        if title.find(u'甩')>-1 or content.find(u'甩')>-1:
#            is_send=True
#        if title.find(u'吐血')>-1 or content.find(u'吐血')>-1:
#            is_send=True
#        if title.find(u'年会')>-1 or content.find(u'年会')>-1:
#            is_send=True
#        if title.find(u'送的')>-1 or content.find(u'送的')>-1:
#            is_send=True

        if title.find(u'cpl')>-1 or content.find(u'cpl')>-1:
            is_send=True
        if title.find(u'b+w')>-1 or content.find(u'b+w')>-1:
            is_send=True
        if title.find(u'B+W')>-1 or content.find(u'B+W')>-1:
            is_send=True
        if title.find(u'渐变')>-1 or content.find(u'渐变')>-1:
            is_send=True
        if title.find(u'滤镜')>-1 or content.find(u'滤镜')>-1:
            is_send=True
        if title.find(u'd700')>-1 and title.find(u'd700')>-1:
            is_send=True

        if is_send:
            import sys
            reload(sys)
            sys.setdefaultencoding('utf8')
            mail_list=['1615990@qq.com']
            psm=Photograph_Subscribe_Message(user_id=11,subscribe_id=1,message_id=msg.id)
            psm.save()
            content=unicode(msg.quality)+u'新  '+unicode(msg.price)+u'元<br/>'+content.replace(u'\n',u'<br>')+\
                    u'<br/><br/>'+msg.url
            send_mutil_email(mail_list,title, content,psm.id)
            #send_single_email('1615990@qq.com',title, content)
