#-*- encoding: utf-8 -*-

from django.contrib import admin
from models import *

class BusinessAdmin ( admin.ModelAdmin ) :
    list_display = ( 'id', 'name', 'chinese_name','submit_url')
    list_display_links =('name','chinese_name','submit_url')
    list_filter = ( 'id', 'name')
    ordering = ('id',)
    search_fields = ( 'id','name')
admin.site.register ( Business, BusinessAdmin )

class SourceSiteAdmin ( admin.ModelAdmin ) :
    list_display = ( 'id', 'domain', 'name')
    list_display_links =('id', 'domain', 'name')
    list_filter = ( 'domain', 'name')
    ordering = ('id',)
    search_fields = ( 'id','domain', 'name')
admin.site.register ( SourceSite, SourceSiteAdmin )

class SpiderParserAdmin ( admin.ModelAdmin ) :
    list_display = ( 'id','module_name', 'class_name','site')
    list_display_links =( 'id','module_name', 'class_name','site')
    list_filter = ( 'id','site', 'class_name')
    ordering = ('id',)
    search_fields = ( 'id','module_name', 'class_name')
admin.site.register ( SpiderParser, SpiderParserAdmin )

class FixTaskAdmin ( admin.ModelAdmin ) :
    list_display = ( 'id','business', 'parser','url','param','last_submit_time')
    list_display_links =('id','parser',)
    list_filter = ( 'parser', )
    ordering = ('id',)
    search_fields = ( 'id','parser')
admin.site.register ( FixTask, FixTaskAdmin )

class RandomTaskAdmin ( admin.ModelAdmin ) :
    list_display = ( 'id','business', 'parser','url','param','state')
    list_display_links =('id','parser',)
    list_filter = ('parser',)
    ordering = ('-id',)
    search_fields = ( 'id','parser')
    list_per_page =10
admin.site.register ( RandomTask, RandomTaskAdmin )

class TaskLogAdmin ( admin.ModelAdmin ) :
    list_display = ( 'id','time', 'parser','task_id','error')
    list_display_links =('id','time', 'parser','task_id','error')
    list_filter = ( 'id','time', 'parser')
    ordering = ('id',)
    search_fields = ( 'id','time', 'parser')
admin.site.register ( TaskLog, TaskLogAdmin )

class SpiderNodeAdmin ( admin.ModelAdmin ) :
    list_display = ( 'id','token', 'name','machine_name','ip','login_times','last_login_time','last_assign_time','total_work_time','finish_task')
    list_display_links =('id','token', 'machine_name','ip')
    list_filter = ( 'id','token', 'machine_name','ip')
    ordering = ('id',)
    search_fields = ( 'id','token', 'machine_name','ip')
admin.site.register ( SpiderNode, SpiderNodeAdmin )

class RunningInfoAdmin ( admin.ModelAdmin ) :
    list_display = ( 'id','table_name', 'fixtask_assign','randomtask_assign','next_assign_time','running_step')
    list_display_links =('id','table_name', 'fixtask_assign','randomtask_assign','next_assign_time','running_step')
    list_filter = ( 'id','table_name')
    ordering = ('id',)
    search_fields = ( 'id','table_name')
admin.site.register ( RunningInfo, RunningInfoAdmin )