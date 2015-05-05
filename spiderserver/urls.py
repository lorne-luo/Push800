#-*- encoding: utf-8 -*-
import os
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'spiderserver.views.home'),

    #--------------------spiderserver---------------------------
    (r'^spiderserver/test/$', 'spiderserver.task.views.test'),
    (r'^spiderserver/gettasks/$', 'spiderserver.task.views.gettasks'),

    (r'^spiderserver/get_fix_task/$', 'spiderserver.task.views.get_fix_task'),
    (r'^spiderserver/pop_fix_task/$', 'spiderserver.task.views.assign_fix_task'),
    (r'^spiderserver/running_status/$', 'spiderserver.task.views.running_status'),
    (r'^spiderserver/last_run_time/$', 'spiderserver.task.views.last_run_time'),

    (r'^spiderserver/get_modules/$', 'spiderserver.task.views.get_modules'),
    (r'^spiderserver/update_modules/$', 'spiderserver.task.views.update_modules'),

    (r'^spiderserver/submittask/$', 'spiderserver.task.views.submittask'),
    (r'^spiderserver/spider_login/$', 'spiderserver.task.views.spider_login'),
    (r'^spiderserver/get_spiders/$', 'spiderserver.task.views.get_spiders'),
    (r'^spiderserver/spiders/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.dirname(os.path.abspath(__file__))+'/task/spiders', 'show_indexes':True}),


    #--------------------------frontserver---------------------------
    (r'^frontserver/message/(?P<business_id>\d+)/(?P<message_id>\d+)/$', 'spiderserver.frontserver.message_views.message'),
    (r'^pe/msg/(?P<business_id>\d+)/(?P<message_id>\d+)/$', 'spiderserver.frontserver.message_views.message'),
    (r'^frontserver/message_list/(?P<business_id>\d+)/$', 'spiderserver.frontserver.message_views.message_list'),
    (r'^frontserver/subscribe_list/(?P<business_id>\d+)/$', 'spiderserver.frontserver.message_views.subscribe_list'),

    (r'^frontserver/add_subscribe/$', 'spiderserver.frontserver.user_views.add_subscribe'),
    (r'^frontserver/create_subscribe/$', 'spiderserver.frontserver.user_views.create_subscribe'),

    (r'^frontserver/subscribes/$', 'spiderserver.frontserver.user_views.subscribes'),

    (r'^frontserver/edit_subscribe/$', 'spiderserver.frontserver.user_views.edit_subscribe'),
    (r'^frontserver/update_subscribe/$', 'spiderserver.frontserver.user_views.update_subscribe'),

    (r'^frontserver/close_subscribe/$', 'spiderserver.frontserver.user_views.close_subscribe'),
    (r'^frontserver/destroy_subscribe/$', 'spiderserver.frontserver.user_views.destroy_subscribe'),

    (r'^frontserver/go_register/$', 'spiderserver.frontserver.user_views.go_register'),
    (r'^frontserver/register/$', 'spiderserver.frontserver.user_views.register'),
    (r'^frontserver/go_validate_register_email/$', 'spiderserver.frontserver.user_views.go_validate_register_email'),
    (r'^frontserver/validate_register_email/$', 'spiderserver.frontserver.user_views.validate_register_email'),
    
    (r'^frontserver/go_login/$', 'spiderserver.frontserver.user_views.go_login'),
    (r'^frontserver/login/$', 'spiderserver.frontserver.user_views.login'),

    (r'^frontserver/go_reset_password_by_email/$', 'spiderserver.frontserver.user_views.go_reset_password_by_email'),
    (r'^frontserver/send_reset_password_email/$', 'spiderserver.frontserver.user_views.send_reset_password_email'),
    (r'^frontserver/go_reset_password/$', 'spiderserver.frontserver.user_views.go_reset_password'),
    (r'^frontserver/reset_password_by_email/$', 'spiderserver.frontserver.user_views.reset_password_by_email'),

    (r'^frontserver/go_modify_password/$', 'spiderserver.frontserver.user_views.go_modify_password'),
    (r'^frontserver/modify_password/$', 'spiderserver.frontserver.user_views.modify_password'),

    (r'^frontserver/subscibe_send_error/$', 'spiderserver.frontserver.message_views.subscribe_send_error_callback'),
    (r'^frontserver/send_email_request/$', 'spiderserver.utils.mail.send_email_request'),

    # test mutil mail
    #(r'^frontserver/mail_test/$', 'spiderserver.utils.mail.mail_test'),
    (r'^img_proxy/', 'spiderserver.frontserver.views.img_proxy'),

    # about page
    (r'^about.html', 'spiderserver.frontserver.views.show_about'),

    #----------------------------------PE-------------------------------
    (r'^pe/(?P<city_name>[a-z]{,6})/$', 'spiderserver.frontserver.message_views.city_msg_list'),
    (r'^pe/(?P<city_name>[a-z]{,6})/search/$', 'spiderserver.frontserver.message_views.advance_search'),#高级搜索
    (r'^pe/(?P<city_name>[a-z]{,6})/subscribe/$', 'spiderserver.frontserver.user_views.add_subscribe'),
    (r'^pe/create_subscribe/$', 'spiderserver.frontserver.user_views.create_subscribe'),

    #-------------------------------resource---------------------------
    (r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.dirname(os.path.abspath(__file__))+'/templates/css', 'show_indexes':False}),
    (r'^img/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.dirname(os.path.abspath(__file__))+'/templates/img', 'show_indexes':False}),
    (r'^js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.dirname(os.path.abspath(__file__))+'/templates/js', 'show_indexes':False}),

    # Examples:
    # url(r'^spiderserver/', include('spiderserver.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)