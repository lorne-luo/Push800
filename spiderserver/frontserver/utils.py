#-*- encoding: utf-8 -*-
#__author__ = 'Administrator'

from models import *

key_hint=u'请输入关键字'

def get_user_by_token(token):
    users = User.objects.filter(perishable_token=token)[:1]
    if len(users):
        return users[0]
    else:
        return None

def get_city(city_id):
    '''
    根据city_id返回City model
    无此id返回None
    '''
    citys = City.objects.filter(id=city_id)[:1]
    if len(citys):
        return citys[0]
    else:
        return None

def get_city_by_name(city_name):
    '''
    根据城市中文名称返回city_id
    如北京返回1
    无此城市中文名则返回None
    '''
    citys = City.objects.filter(name_cn=city_name)[:1]
    if len(citys):
        return citys[0]
    else:
        return None
def get_city_by_shortname(city_shortname):
    '''
    根据拼音首字母的缩写返回city_id
    如bj返回1
    无此缩写返回None
    '''
    citys = City.objects.filter(name_ab=city_shortname)[:1]
    if len(citys):
        return citys[0]
    else:
        return None

def get_user_by_phonenumber(phone_number):
    '''通过手机号码查找用户，若没有返回None'''
    user_list=User.objects.filter(phone_number=(phone_number))[:1]
    if len(user_list):
        return user_list[0]
    else:
        return None

def get_user_by_email(e):
    '''通过email查找用户，若没有返回None'''
    user_list=User.objects.filter(email=e)[:1]
    if len(user_list):
        return user_list[0]
    else:
        return None

def get_brand_by_name(name):
    '''根据品牌名获得品牌model,若不存在返回None'''
    brand_list=Photograph_Brand.objects.filter(name_cn=name)[:1]
    if len(brand_list):
        return brand_list[0]
    else:
        return None