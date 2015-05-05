#-*- encoding: utf-8 -*-

from django.contrib import admin
from models import *

class BusinessAdmin ( admin.ModelAdmin ) :
    list_display = ( 'id', 'name', 'chinese_name','submit_url')
    list_display_links =('name','chinese_name','submit_url')
    ordering = ('id',)
    search_fields = ( 'id','name')
admin.site.register ( Business, BusinessAdmin )

class UserAdmin ( admin.ModelAdmin ) :
    list_display = ( 'id', 'username', 'email', 'phone_number', 'city_id', )
    list_display_links = ('id', 'username', 'email')
    ordering = ('-id',)
    search_fields = ( 'id','username','email')
admin.site.register ( User, UserAdmin )

class CityAdmin ( admin.ModelAdmin ) :
    list_display = ( 'id','name_cn', 'name_py','name_ab')
    list_display_links =('id','name_cn', 'name_py','name_ab')
    ordering = ('id',)
    search_fields = ( 'id','name_cn', 'name_py','name_ab')
admin.site.register ( City, CityAdmin )

class City_DistrictAdmin ( admin.ModelAdmin ) :
    list_display = ( 'id','city','name_cn', 'name_py','name_ab')
    list_display_links =('id','city','name_cn', 'name_py','name_ab')
    list_filter = ( 'city',)
    ordering = ('id',)
    search_fields = ( 'id','city','name_cn', 'name_py','name_ab')
admin.site.register ( City_District, City_DistrictAdmin )

class Photograph_BrandAdmin ( admin.ModelAdmin ) :
    list_display = ( 'id','name_cn','name_en', 'name_py','name_ab')
    list_display_links =('id','name_cn','name_en', 'name_py','name_ab')
    list_filter = ( 'name_cn',)
    ordering = ('id',)
    search_fields = ( 'id','name_cn','name_en', 'name_py','name_ab')
admin.site.register ( Photograph_Brand, Photograph_BrandAdmin )

class Photograph_SubscribeAdmin ( admin.ModelAdmin ) :
    list_display = ( 'id','user_id', 'city_id','district_id','keyword','min_price','max_price')
    list_display_links =('id','user_id','city_id','keyword')
    list_filter = ('city_id',)
    ordering = ('-id',)
    search_fields = ( 'id','user_id', 'city_id','keyword')
    list_per_page =20
admin.site.register ( Photograph_Subscribe, Photograph_SubscribeAdmin )

class Photograph_MessageAdmin ( admin.ModelAdmin ) :
    list_display = ( 'id','city','url','publish_time','title')
    list_display_links =('id','city', 'publish_time','title')
    #list_filter = ( )
    ordering = ('-id',)
    search_fields = ( 'id','publish_time','url','title')
    list_per_page =20
admin.site.register ( Photograph_Message, Photograph_MessageAdmin )

class Photograph_Subscribe_MessageAdmin ( admin.ModelAdmin ) :
    list_display = ( 'id','user_id','subscribe_id', 'message_id')
    list_display_links =('id','user_id','subscribe_id', 'message_id')
    ordering = ('-id',)
    search_fields = ( 'id','user','subscribe', 'message')
    list_per_page =20
admin.site.register ( Photograph_Subscribe_Message, Photograph_Subscribe_MessageAdmin )

class PictureAdmin ( admin.ModelAdmin ) :
    list_display = ( 'id','url','data')
    list_display_links =('id','url','data')
    ordering = ('-id',)
    search_fields = ( 'id','url','data')
admin.site.register ( Picture, PictureAdmin )


