#-*- encoding: utf-8 -*-
from django.db import models
from spiderserver.task.models import SourceSite


class Business(models.Model):
    name = models.CharField(max_length=30)
    chinese_name = models.CharField(max_length=30)
    message_format = models.TextField()
    submit_url = models.URLField(verify_exists=False)
    introduce = models.TextField(null=True, blank=True)
    def __unicode__(self):
        return "[%s]%s" % (self.id,self.chinese_name)

class City(models.Model):
    name_cn = models.CharField(max_length=30,null=False,blank=False)#
    name_py = models.CharField(max_length=30,null=False,blank=False)#拼音
    name_ab = models.CharField(max_length=10,null=True,blank=True)#缩写或别称
    def __unicode__(self):
        return "[%d]%s" % (self.id,self.name_cn)
    
class City_District(models.Model):
    city = models.ForeignKey(City, null=False, blank=False, related_name='district_city')
    name_cn = models.CharField(max_length=30,null=False,blank=False)#
    name_py = models.CharField(max_length=30,null=False,blank=False)#拼音
    name_ab = models.CharField(max_length=10,null=True,blank=True)#缩写或别称
    def __unicode__(self):
        return "[%d]%s-%s" % (self.id,self.city.name_cn,self.name_cn)
    
class Photograph_Brand(models.Model):
    name_cn = models.CharField(max_length=30,null=False,blank=False)#
    name_en = models.CharField(max_length=30,null=False,blank=False)#英文
    name_py = models.CharField(max_length=30,null=False,blank=False)#拼音
    name_ab = models.CharField(max_length=30,null=True,blank=True)#缩写或别称
    def __unicode__(self):
        return "[%d]%s" % (self.id,self.name_cn)

class User(models.Model):
    username = models.CharField(max_length=72, blank=True)
    nick_name = models.CharField(max_length=72, blank=True)
    hashed_password = models.CharField(max_length=384, blank=True)
    password_salt = models.CharField(max_length=120, blank=True)
    perishable_token = models.CharField(max_length=150, blank=True)
    register_time = models.DateTimeField(null=True, blank=True)
    register_ip = models.IntegerField(null=True, blank=True)
    failed_login_count = models.IntegerField(null=True, blank=True)
    current_login_ip = models.CharField(max_length=45, blank=True)
    last_login_time = models.DateTimeField(null=True, blank=True)
    last_request_time = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.CharField(max_length=45, blank=True)
    email = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=45, blank=True)
    phone_ime = models.CharField(max_length=600, blank=True)
    status = models.IntegerField(null=True, blank=True)
    user_type = models.IntegerField(null=True, blank=True)
    user_auth = models.IntegerField(null=True, blank=True)
    gender = models.IntegerField(null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    avatar = models.CharField(max_length=120, blank=True)
    city_id = models.IntegerField(null=True, blank=True)
    district_id = models.IntegerField(null=True, blank=True)
    subscribe_status = models.IntegerField(null=True, blank=True)
    online_time = models.IntegerField(null=True, blank=True)
    invite_code = models.CharField(max_length=60, blank=True)
    identity_status = models.IntegerField(null=True, blank=True)
    password_to_reset = models.CharField(max_length=384, blank=True)
    def __unicode__(self):
        return "[%d]%s" % (self.id,self.username)
    
class Photograph_Subscribe(models.Model):
    user_id = models.IntegerField()
    city_id = models.BigIntegerField(null=True, blank=True)
    district_id = models.BigIntegerField(null=True, blank=True,default=0)
    brand_id = models.BigIntegerField(null=True, blank=True)
    min_price = models.IntegerField(null=True, blank=True)
    max_price = models.IntegerField(null=True, blank=True)
    keyword = models.CharField(null=True, max_length=300, blank=True)
    email = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True,default=0)#0代表此订阅已已经关闭，1代表进行中
    close_at = models.DateTimeField(null=True, blank=True)
    notify_count = models.IntegerField(null=True, blank=True,default=0)
    def __unicode__(self):
        return "[%d] user_id=%s keyword=%s city_id=%s district_id=%s" % (self.id, self.user_id, self.keyword, self.city_id, self.district_id)

class Photograph_Message(models.Model):
    city = models.CharField(max_length=30,null=False,blank=False)
    city_id =  models.BigIntegerField(null=False,blank=False,default=0)#城市id
    district = models.CharField(max_length=30,null=True,blank=True)
    district_id = models.BigIntegerField(null=False,blank=False,default=0)#城区id
    brand_id = models.BigIntegerField(null=False,blank=False,default=0)#品牌id
    url = models.URLField(null=False, blank=False,verify_exists=False)
    site = models.ForeignKey(SourceSite, null=False, blank=False, related_name='message_site')
    publish_time = models.DateTimeField(null=False,blank=False)
    price = models.IntegerField(null=True,blank=True,default=0)
    quality = models.SmallIntegerField(null=True,blank=True,default=0)
    title = models.CharField(max_length=100,null=True,blank=True)
    contact = models.TextField(null=True,blank=True)
    content = models.TextField(null=True, blank=True)
    seller = models.CharField(max_length=100,null=True,blank=True)
    is_sell = models.BooleanField(null=False,blank=False,default=1)#True出售 False求购
    picture = models.TextField(null=True, blank=True)
    show_count = models.IntegerField(null=True,blank=True,default=0)#消息被送去提醒的次数
    is_spam=models.BooleanField(null=False,blank=False,default=0)#是否是spam
    task_id=models.BigIntegerField(null=True,blank=True,default=0)#randomtask的id
    create_time = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return "[%d]%s" % (self.id,self.title)
    
class Photograph_Subscribe_Message(models.Model):
    user_id = models.BigIntegerField(null=False,blank=False,default=0)
    subscribe_id = models.BigIntegerField(null=False,blank=False,default=0)
    message_id = models.BigIntegerField(null=False,blank=False,default=0)
    favorite = models.BooleanField(null=False,default=False)
    review = models.SmallIntegerField(null=False,default=0)
    def __unicode__(self):
        return "[%d]%d-%d" % (self.user_id,self.subscribe_id,self.message_id)

class Picture(models.Model):
    url = models.URLField(null=False, blank=False,verify_exists=False)
    data = models.TextField(null=True, blank=True)
    def __unicode__(self):
        return "[%d]%s" % (self.id,self.url)
    
    
    