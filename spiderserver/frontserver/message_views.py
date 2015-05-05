#-*- encoding: utf-8 -*-
'''
Created on 2011-11-30
@author: Leo

这里所有函数均是对subscribe和message的展示和处理
所有response都需要通过html进行展示
'''
from models import *
import json,urllib,datetime
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse
import utils
import search_func
from django.core.paginator import PageNotAnInteger, Paginator, InvalidPage, EmptyPage
from django.db.models import Avg, Max, Min, Count
from sae.taskqueue import add_task


def subscribe(request,subscribe_id):
    subscribe_id=int(subscribe_id)
    pass

def subscribe_list(request,business_id):
    '''
    展示某用户当前进行中的任务和历史完成过的订阅任务
    http://leandro.132.china123.net/android/push800/html/task_list.htm
    http://push800.sinaapp.com/frontserver/subscribe_list/1/?user_token=6.20565686525
    '''
    business_id=int(business_id)
    user=None
    if request.GET.has_key('user_token'):
        token=request.GET['user_token']
        user=utils.get_user_by_token(token)
    elif request.GET.has_key('phone_number'):
        phone_number=request.GET['phone_number']
        user=utils.get_user_by_phonenumber(phone_number)
    else:
        return HttpResponse('NO USER_TOKEN or PHONE_NUMBER POSTED')

    if user is None:
        return HttpResponse('NO USER')
    
    sub_list=[]
    template_name=''
    if business_id==1:
        sub_list = Photograph_Subscribe.objects.filter(user_id=user.id).order_by('-id')[:10]
        template_name = 'subscribe_list.html'
        for sub in sub_list:
            sub.city_name=utils.get_city(sub.city_id).name_cn
            sub.created_at=sub.created_at.strftime('%m-%d')
            sub.updated_at=sub.updated_at.strftime('%m-%d')
    elif business_id==2:
        #其他业务
        return HttpResponse('NO BUSINESS ID == 2')
    return render_to_response(template_name, {'sub_list': sub_list})

def message(request,business_id,message_id):
    """
    展示最新一条msg内容
    http://leandro.132.china123.net/android/push800/html/message.htm
    http://push800.sinaapp.com/frontserver/message/1/123/
    """
    try:
        business_id=int(business_id)
        message_id=int(message_id)
        msg=None
        template_name=''
        if business_id==1:
            msg = Photograph_Message.objects.get(id=message_id)
            msg.publish_time=msg.publish_time.strftime('%m-%d %H:%M')
            if msg.district!='':
                msg.city=msg.city+'-'+msg.district
            if msg.price<1:
                msg.price=u'价格面议'
            else:
                msg.price=str(msg.price)

            if msg.quality>0:
                if msg.quality==100:
                    msg.quality=u'全新'
                elif msg.quality%10==0:
                    msg.quality=str(msg.quality/10)+u'成新'
                else:
                    msg.quality=str(msg.quality)+u'成新'
                msg.price=msg.quality+' '+msg.price

            try:
                #格式化联系方式
                contact=json.loads(msg.contact)
                if type(contact) is str or type(contact) is unicode:
                    msg.contact=contact
                elif type(contact) is list:
                    contact_str=''
                    for c in contact:
                        if len(c)==2:
                            if msg.site_id==4:#淘宝有防盗链措施
                                contact_str+=c[0]+':<img src="/img_proxy/?url='+c[1]+'"><br/>'
                            elif c[1].startswith('http:'):
                                contact_str+=c[0]+':<img src="'+c[1]+'"><br/>'
                            else:
                                contact_str+=c[0]+':'+c[1]+'<br/>'
                    msg.contact=contact_str
                if msg.contact=='':
                    msg.contact=u'请访问 <a href="'+msg.url+u'"><u>原始信息</u></a> 查看联系方式'
            except :
                pass
            msg.content=msg.content.replace('\n','<br/>')

            try:
                #格式化图片
                pics=json.loads(msg.picture)
                pic_str=''
                if type(pics) is list:
                #蜂鸟的图片防盗链，取消不显示
                    if msg.site_id==1:
                        for p in pics:
                            pic_str+='<img style="float:left" width="220" src="/img_proxy/?url='+p+'">\n'
                    else:
                        for p in pics:
                            pic_str+='<img style="float:left" width="220" src="'+p+'">\n'
                msg.picture=pic_str
            except :
                pass
            template_name = 'photograph_message.html'
        elif business_id==2:
            #其他业务
            pass
        brand_list=Photograph_Brand.objects.all()
        city=utils.get_city(msg.city_id)
        if city is None:
            city=City()
            city.id=0
            city.name_cn=''
            city.name_ab=''
        city_list=City.objects.filter(id__lt=6)
        return render_to_response(template_name, {'msg': msg,'city': city,'city_list':city_list,'brand_list':brand_list})
    except Exception,e:
        return HttpResponse(str(e))

def message_list(request,business_id):
    '''
    展示msg的列表，点击任意的subscribe记录到达此页面
    http://leandro.132.china123.net/android/push800/html/message_list.htm
    http://push800.sinaapp.com/frontserver/message_list/1/?user_token=9.708855216547
    '''

    business_id=int(business_id)
    token=None
    if request.GET.has_key('user_token'):
        token=request.GET['user_token']
    elif request.POST.has_key('user_token'):
        token=request.POST['user_token']
    else:
        return HttpResponse('NO USER_TOKEN POSTED')

    user=utils.get_user_by_token(token)
    if user is None: return HttpResponse('NO THIS USER')
    msg_list=[]
    template_name=''
    if business_id==1:
        psm_list = Photograph_Subscribe_Message.objects.filter(user_id=user.id).order_by('-id')[:10]
        for msg in psm_list:
            try:
                m=Photograph_Message.objects.get(id=msg.message_id)
                if m.district!='':#若城区信息不为空则将城市和城区信息合并显示
                    m.city=m.city+'|'+m.district
                m.publish_time=m.publish_time.strftime('%m-%d %H:%M')#格式化时间
                m.url='/pe/msg/1/'+str(m.id)+'/'
                msg_list.append(m)
            except :
                continue
        template_name = 'message_list.html'
    elif business_id==2:
        return HttpResponse('NO BUSINESS ID == 2')
    return render_to_response(template_name, {'msg_list': msg_list})


def city_msg_list(request,city_name):
    '''城市版面信息列表，包括查询'''
    #查询城市id
    if city_name=='' or city_name is None:
        city=None
    else:
        city=utils.get_city_by_shortname(city_name)

    params=request.GET
    #可能有查询字段brand_id和keyword
    brand_id=int(params['brand_id']) if params.has_key('brand_id') and params['brand_id'].isdigit() else 0
    keyword=urllib.unquote_plus(params['keyword'].replace('%20','+')) if params.has_key('keyword') and params['keyword']!=''  else utils.key_hint
    phone_number=int(params['phone_number']) if params.has_key('phone_number') and params['phone_number'].isdigit() else 0
    phone_ime=params['phone_ime'] if params.has_key('phone_ime') else ''
    min_price=int(params['min_price']) if params.has_key('min_price') and params['min_price'].isdigit() else 0
    max_price=int(params['max_price']) if params.has_key('max_price') and params['max_price'].isdigit() else 0
    quality=int(params['quality']) if params.has_key('quality') and params['quality'].isdigit() else 0

    #获取页数
    try:
        page = int(request.GET.get("page",1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    messages=[]
    #todo这里需要对记录列表进行分页
    if city is None:
        #如果没有城市信息则不区分城市，查询所有记录
        search_day=datetime.datetime.now()-datetime.timedelta(seconds=1728000)
        msg_list=Photograph_Message.objects.all().order_by('-id')[0:600]
        city=City()
        city.id=0
        city.name_cn=''
    else:
        if brand_id==0 and (keyword==utils.key_hint or keyword=='') and min_price==0 and max_price==0 and quality==0:
            search_day=datetime.datetime.now()-datetime.timedelta(seconds=1728000)
            msg_list=Photograph_Message.objects.filter(city_id=city.id).order_by('-id')[0:600]
        else:
            k='' if keyword==utils.key_hint else keyword
            try:
                msg_list=search_func.search_message(city.id,brand_id,min_price,max_price,quality,k.encode('utf-8'))[0:600]
            except Exception,e:
                return HttpResponse(e)

    # 设置books在每页显示的数量，这里为20
    paginator = Paginator(msg_list,20)

    try:
        #跳转到请求页面，如果该页不存在或者超过则跳转到尾页
        messages = paginator.page(page)
    except(EmptyPage,InvalidPage,PageNotAnInteger):
        messages = paginator.page(paginator.num_pages)

    after_range_num = 5        #当前页前显示5页
    befor_range_num = 4       #当前页后显示4页
    if page >= after_range_num:
        page_range = paginator.page_range[page-after_range_num:page+befor_range_num]
    else:
        page_range = paginator.page_range[0:int(page)+befor_range_num]


    for m in messages.object_list:
        if m.district!='':#若城区信息不为空则将城市和城区信息合并显示
            m.city=m.city+'-'+m.district
        m.publish_time=m.publish_time.strftime('%m-%d %H:%M')#格式化时间
        m.url='/pe/msg/1/'+str(m.id)+'/'
        if m.quality<10:
            m.price=str(m.price)
        else:
            m.price=str(m.quality)+'新/'+str(m.price)

        pics=None
        try:
            pics=json.loads(m.picture)
        except :
            pass
        if type(pics) is list and len(pics)>0:
            m.picture=len(pics)
        else:
            m.picture=0

    #品牌列表
    brand_list=Photograph_Brand.objects.all()
    city_list=City.objects.filter(id__lt=6)
    return render_to_response('city_message_list.html', {'msg_list': messages,'city':city,
                    'min_price':min_price,'max_price':max_price,'page_range':page_range,'city_list':city_list,
                    'quality':quality,'brand_id':brand_id,'keyword':keyword,'brand_list':brand_list,
                    'phone_number':phone_number,'phone_ime':phone_ime})

def advance_search(request,city_name):
    '''城市版面高级查询'''
    #查询城市id
    if city_name=='' or city_name is None:
        city=None
    else:
        city=utils.get_city_by_shortname(city_name)

    params=request.GET
    #可能有查询字段brand_id和keyword
    brand_id=int(params['brand_id']) if params.has_key('brand_id') and params['brand_id'].isdigit() else 0
    keyword=urllib.unquote_plus(params['keyword'].replace('%20','+')) if params.has_key('keyword') else ''
    phone_number=int(params['phone_number']) if params.has_key('phone_number') and params['phone_number'].isdigit() else 0
    phone_ime=params['phone_ime'] if params.has_key('phone_ime') else ''
    min_price=int(params['min_price']) if params.has_key('min_price') and params['min_price'].isdigit() else 0
    max_price=int(params['max_price']) if params.has_key('max_price') and params['max_price'].isdigit() else 0
    page=params['page'] if params.has_key('page') and params['page'].isdigit() else 0

    if city is None:
        city=City()
        city.id=0
        city.name_cn=''
        city.name_ab=''

    #品牌列表
    brand_list=Photograph_Brand.objects.all()
    district_list=City_District.objects.filter(city=city.id)
    city_list=City.objects.filter(id__lt=6)
    return render_to_response('advance_search.html', {'city':city,'city_list':city_list,
                            'phone_number':phone_number,'phone_ime':phone_ime,
                            'min_price':min_price,'max_price':max_price,
                'brand_id':brand_id,'keyword':keyword,'brand_list':brand_list,'district_list':district_list})

def add_message(business_id,msg,task_id):
    """
    添加新的msg
    """
    if business_id==1:
        try:
            price=int(msg['Price'])
        except:
            price=-1
        try:
            quality=int(msg['Quality'])
        except:
            quality=0

        if quality==0 and msg['Title'].find(u'全新')>0:
            quality=100
        elif quality>100:
            quality=100

        try:
            district_id=int(msg['District_id'])
        except:
            district_id=0
        try:
            city_id=int(msg['City_id'])
        except:
            city_id=0
        try:
            brand_id=int(msg['Brand_id'])
        except:
            brand_id=29

        try:
            #先依据url检查是否有重复的数据
            max_id=Photograph_Message.objects.aggregate(max_id=Max('id'))['max_id']#查出现在最大id号
            max_id-=1000 #只检查最近1000条中是否有重复
            dup_count=Photograph_Message.objects.filter(id__gte=max_id,url=msg['Url']).order_by('id')

            if dup_count:
                return False,'dup data='+msg['Url']+' old_id='+str(dup_count[0].id)

            pm=Photograph_Message(city=msg['City'],
                                  city_id=city_id,
                                  district=msg['District'],
                                  district_id=district_id,
                                  url=msg['Url'],
                                  site_id=msg['Site_id'],
                                  publish_time=msg['Time'],
                                  price=price,
                                  quality=quality,
                                  title=msg['Title'],
                                  content=msg['Content'],
                                  contact=json.dumps(msg['Contact'], ensure_ascii=False),
                                  seller=msg['Seller'],
                                  is_sell=msg['Is_sell'],
                                  brand_id=brand_id,
                                  picture=json.dumps(msg['Pics'], ensure_ascii=False),
                                  task_id=task_id
                                  )
            pm.save()

            try:
                search_func.search_subscribe(pm)
            except Exception,e:
                pass

        except Exception,e:
            return False,u'msg add err:'+str(e)

        try:
            for p in msg['Pics']:
                pic=Picture(url=p)
                pic.save()
        except Exception,e:
            return False,u'pic store err:'+str(e)

        return True,''

def subscribe_send_error_callback(request):
    '''发送完订阅邮件失败的回调函数'''
    trycount=int(request.POST['trycount']) if request.POST.has_key('trycount') else 3
    psm_id=int(request.POST['psm_id']) if request.POST.has_key('psm_id') else 0
    if trycount<3:
        #重试
        trycount+=1
        email_address=request.POST['email_address'] if request.POST.has_key('email_address') else None
        subject=request.POST['subject'] if request.POST.has_key('subject') else None
        html=request.POST['html'] if request.POST.has_key('html') else None
        postdata='email_address=%s&subject=%s&html=&s&psm_id=%d&trycount=%d'%(email_address, subject, html,psm_id,trycount)
        add_task('MailQueue', '/frontserver/send_email_request/', postdata)
        return HttpResponse('RETRY = '+str(trycount))
    else:
        #todo 置为失败
        return HttpResponse('RETRY=3 SEND FAILED')
