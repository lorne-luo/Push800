#-*- encoding: utf-8 -*-
from django.db import models
import datetime
# Create your models here.

class Business(models.Model):
    name = models.CharField(max_length=30)
    chinese_name = models.CharField(max_length=30,verbose_name='chinese name' )
    message_format = models.TextField()
    submit_url = models.URLField(verify_exists=False)
    introduce = models.TextField(null=True, blank=True)
    def __unicode__(self):
        return "[%d]%s" % (self.id,self.chinese_name)

class SourceSite(models.Model):
    domain = models.CharField(max_length=30,null=False,blank=False)#域名
    name = models.CharField(max_length=30,null=False,blank=False)#中文名称
    def __unicode__(self):
        return "[%d]%s" % (self.id,self.name)

class SpiderParser(models.Model):
    module_name = models.CharField(max_length=50,null=False, blank=False)
    class_name = models.CharField(max_length=50,null=False, blank=False)
    site = models.ForeignKey(SourceSite, null=False, blank=False, related_name='parser_site')
    param_format = models.CharField(max_length=300,null=True, blank=True)
    param_count = models.IntegerField(null=True, blank=True)
    source_code = models.TextField(null=True, blank=True)
    version = models.IntegerField(default=1,null=False, blank=False)
    def __unicode__(self):
        return "[%d]%s" % (self.id,self.class_name)
    
class FixTask(models.Model):
    parser = models.ForeignKey(SpiderParser, null=False, blank=False, related_name='fixtask_parser')
    next_parser = models.ForeignKey(SpiderParser, null=True, blank=True, related_name='fixtask_next_parser')
    #method_name = models.CharField(max_length=50,null=False, blank=False, unique=True)
    #next_method_name = models.CharField(max_length=50, blank=True)
    business = models.ForeignKey(Business, null=False, blank=False, related_name='fixtask_business')
    #domain = models.ForeignKey(SourceSite, null=False, blank=False, related_name='fixtask_site')
    domain = models.CharField(max_length=50,blank=True)#顶级域名
    url = models.URLField(null=False, blank=False,verify_exists=False)
    param = models.TextField(null=False,blank=True)
    last_assign_time = models.DateTimeField(default=datetime.datetime(1970,1,1))
    last_submit_time = models.DateTimeField(default=datetime.datetime(1970,1,1))
    interval = models.SmallIntegerField(null=False,default=300)#间隔时间
    enable = models.BooleanField(null=False,default=False)#是否启用
    assign_times = models.SmallIntegerField(null=False,default=0)#分配任务的次数
    submit_times = models.SmallIntegerField(null=False,default=0)#提交任务次数
    message_count = models.SmallIntegerField(null=False,default=0)#新消息条数
    error_count = models.SmallIntegerField(null=False,default=0)#连续异常次数
    note = models.TextField(null=True,blank=True)#备注
    modify_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return "[%d]%s" % (self.id,self.parser.class_name)
    
class RandomTask(models.Model):
    fixtask = models.ForeignKey(FixTask, null=False, blank=False, related_name='fixtask_randomtask')
    parser = models.ForeignKey(SpiderParser, null=False, blank=False, related_name='randomtask_parser')
    pre_parser = models.ForeignKey(SpiderParser, null=True, blank=True, related_name='randomtask_pre_parser')
    next_parser = models.ForeignKey(SpiderParser, null=True, blank=True, related_name='randomtask_next_parser')
    business = models.ForeignKey(Business, null=False, blank=False, related_name='randomtask_business')
    url = models.URLField(null=False, blank=False,verify_exists=False)
    param = models.TextField(null=False,blank=True)#自管理参数
    #state -1爬行页面失败 0任务还需要分配 1任务已经执行完毕 2已经提交至前台数据库
    state = models.SmallIntegerField(null=False,default=0)
    pre_result = models.TextField(null=False,blank=True)#任务执行结果
    last_assign_time = models.DateTimeField(default=datetime.datetime(1970,1,1))
    last_submit_time = models.DateTimeField(default=datetime.datetime(1970,1,1))
    assign_times = models.SmallIntegerField(null=False,default=0)#分配任务的次数
    error_count = models.SmallIntegerField(null=False,default=0)#连续异常次数
    note = models.TextField(null=True,blank=True)#备注
    modify_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return "[%d]%s" % (self.id,self.last_submit_time)
    
class TaskLog(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    parser = models.ForeignKey(SpiderParser, null=False, blank=False, related_name='log_parser')
    task_id = models.IntegerField(null=False, blank=False)
    error = models.TextField(null=True,blank=True)
    def __unicode__(self):
        return "%s %s[%d]=%s" % (self.time,self.parser.class_name,self.task_id,self.error)

class SpiderNode(models.Model):
    token = models.CharField(max_length=30,null=False,blank=False)
    name = models.CharField(max_length=50,null=True,blank=True)
    ip = models.CharField(max_length=20,null=False,blank=False)
    machine_name = models.CharField(max_length=50,null=False,blank=False)
    login_times = models.SmallIntegerField(null=True,blank=True,default=0)
    last_login_time = models.DateTimeField(default=datetime.datetime(1970,1,1))
    last_assign_time = models.DateTimeField(default=datetime.datetime(1970,1,1))
    total_work_time = models.FloatField(null=True,blank=True,default=0)
    finish_task = models.SmallIntegerField(null=True,blank=True,default=0)
    def __unicode__(self):
        name=self.name if self.name=='' or self.name==None else self.machine_name
        return "[%s][%s]" % (self.token,name)
    
class RunningInfo(models.Model):
    table_name = models.CharField(max_length=30,null=False,blank=False)
    fixtask_assign = models.TextField(null=False,blank=False,default='{}')
    randomtask_assign = models.TextField(null=False,blank=False,default='{}')
    next_assign_time = models.DateTimeField(default=datetime.datetime(1970,1,1))
    running_step = models.SmallIntegerField(null=False,blank=False,default=0)
    heartbreak_sec = models.SmallIntegerField(null=False,blank=False,default=0)
    node_count = models.SmallIntegerField(null=False,blank=False,default=0)
    def __unicode__(self):
        return "[%s]%s" % (self.id,self.table_name)
