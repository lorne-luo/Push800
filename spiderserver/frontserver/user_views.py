#-*- encoding: utf-8 -*-
"""
Created on 2011-11-30
@author: Leo

此views全部是与用户注册信息打交道的request处理，
因为目前不考虑推出web端，所以这里所有处理函数不需要写提交页面，不需要返回html页面，只需要做处理post的逻辑
提交post的人机交互界面由手机端负责实现
这里request和response的数据格式需要给王昊提交一份详细文档，返回给手机端的response统一用json格式
"""
import random
import re
from django.http import HttpResponse
from django.shortcuts import render_to_response
import time
import utils
from django.template.loader import get_template
from models import *
import datetime,json,urllib
from sae.mail import EmailMessage
from django.template import Template, Context
from django.core import serializers

#TODO 这里是不是要放在另一个地方
Status_Passive = 0
Status_Pending = 1
Status_Activated = 2
Status_Suspended = 3
Status_Deleted = 4
Status_Desc = {
    Status_Passive : "被动", #默认的初始状态
    Status_Pending : "未激活", #激活但未登录：点击了邮件验证激活连接，但没有成功登录过
    Status_Activated : "已激活", #登录过
    Status_Suspended : "已屏蔽", #有问题的用户
    Status_Deleted : "已删除", #不可再使用了，按照道理，这个用户名应该转让出来，供别人使用
}

Identity_Status_Unknown = 0
Identity_Status_Email = 1
Identity_Status_Phone = 2
Identity_Status_Desc = {
    Identity_Status_Unknown : '未验证',
    Identity_Status_Email : '邮箱验证',
    Identity_Status_Phone : '手机验证'
}
SITE_NAME_CHN = "Push800"
SITE_NAME = "push800"
SITE_HOME = "http://push800.sinaapp.com"
SITE_FRONT_HOME = "%s/frontserver" % SITE_HOME

#------------------------- 注册登录接口 --------------------------#
def go_login(request):
    """

    """
    return render_to_response('login.html', {})

def login(request):
    """
    处理登录请求
    用户名or电子邮箱登录均可
    每次登录给app返回一个token，登录后app对服务器的任何请求都以token为登录凭证（或者session实现？）

    登录的用例：
    用户：
      用户名or电子邮箱登录
    服务器：
      用户输入的格式判断
      判断输入的是用户名还是email（用户名不能有@符号）
      根据username和password选择用户，如果不存在则退出
      OK1: 是正确用户，需要判断用户状态，是不是email验证过了
      OK2: 登录成功
           需要判断用户原来的状态是不是：已经验证但未激活，如果是需要改为已经激活状态
    """
    params = request.POST
    error_str = "请输入正确的用户名和密码"
    errors = [error_str]
    return_hash = {'success':False, 'error':errors, 'user_token':''}


    if not (key_exist(params, 'login_id') and key_exist(params, 'password')):
        return HttpResponse(json.dumps(return_hash, ensure_ascii=False))

    login_id = params['login_id']
    password = params['password']

    user = get_user_by_login_id(login_id)
    if not user:
        return HttpResponse(json.dumps(return_hash, ensure_ascii=False))

    hashed_password = encrypt_password(password, user.password_salt)
    if user.hashed_password != hashed_password:
        return HttpResponse(json.dumps(return_hash, ensure_ascii=False))

    return_hash['success'] = True
    return_hash['user_token'] = user.perishable_token
    return_hash['error'] = []
    if user.status == Status_Pending:
        user.status = Status_Activated
        user.save()
    return HttpResponse(json.dumps(return_hash, ensure_ascii=False))

def go_register(request):
    return render_to_response('register.html')

def register(request):
    """
    处理注册请求
    邮箱必填，如果用户愿意，还可以选填一个简短的用户名，方便登录时输入，
    其他注册时需要的信息，参考model的User表，除了邮箱和密码是必填外其余都是选填
    手机端会同时把手机的串码提交上来
    同意用户协议就先不用了，别人app上也很少看见

    注册的用例：
    #用户：
    #  输入帐号+密码+确认密码+相关的必要选项比如同意网站条款等
    #服务器：
    #  提交后服务器端验证：用户输入符合格式|帐号唯一|密码和确认密码一致
    #  服务器为密码生成salt值|加密的密码
    #  生成perishable_token给email验证使用
    #  发送email(包含加密过的用户名和perishable_token)
    #  email发送成功后，跳转到XXX页面
    """
    if request.method == 'GET':
        return HttpResponse("404 Not Found")

    params = request.POST
    errors = []
    return_hash = {'success':False, 'error':errors, 'user_token':''}

    validate_register_params(params, errors)
    if errors:
        return HttpResponse(json.dumps(return_hash, ensure_ascii=False))

    password_salt = gene_random_code()
    perishable_token = gene_random_code()
    hashed_password = encrypt_password(params['password'], password_salt)

    user = User()
    if params.has_key('username'): user.username = params['username']
    user.hashed_password = hashed_password
    user.password_salt = password_salt
    user.perishable_token = perishable_token
    user.register_time = datetime.datetime.now()
    user.email = params['email']
    if params.has_key('phone_number'): user.phone = params['phone_number']
    if params.has_key('phone_ime'): user.phone_ime = params['phone_ime']
    user.status = 0
    if params.has_key('city_id'): user.city_id = params['city_id']
    if params.has_key('district_id'): user.district_id = params['district_id']

    if not send_register_validate_email(user):
        errors.append("验证邮件发送失败")
        return HttpResponse(json.dumps(return_hash, ensure_ascii=False))

    user.save() #这里怎么验证保存成功了 TODO Lijungang???

    return_hash['success'] = True
    return_hash['user_token'] = user.perishable_token
    return HttpResponse(json.dumps(return_hash, ensure_ascii=False))

def send_register_validate_email(user):
    '''
    
    '''
    if user.username:
        login_id = user.username
    elif user.email:
        login_id = user.email
    else:
        login_id = user.phone_number

    confirm_url = "%s/validate_register_email?login_id=%s&validate_code=%s" % (SITE_FRONT_HOME, login_id, user.perishable_token)
    t = get_template('send_register_email.html')
    html = t.render(Context({'confirm_url': confirm_url, 'user': user, 'login_id': login_id}))
    send_email(user.email, "Push800注册确认邮件", html)
    return True

def go_validate_register_email(request):
    return render_to_response('validate_email.html', {})

def validate_register_email(request):
    '''
    响应用户从邮箱中点击的验证连接，验证邮箱
    验证email的用例：
    用户：
        用户从邮箱点击发送过去的验证连接
        需要跳转到一个新页面
        #1 验证成功，则返回成功页面，例如到达登录页面，让用户登录，或者直接就登录了
        #2 验证不成功的，返回失败信息
        #3 对于手机端，则只需要返回信息就行，不许要跳转页面
    服务器：
        验证用户名+验证token联合存在
        结果：
        #1 验证成功
        #2 验证是攻击用户伪造的，验证失败。（少有）
        #3 重复验证，这个用户其实已经验证过了，但是用户忘记了等等，又点击了一下。（少有）: 只要没有成功登录，这是允许的
    其他：
        验证应该用get请求，原因：
          有时候邮箱，尤其是某些控制严格的邮箱，不允许发送的信息带有可点击的a标签（或者过滤了）
          很多邮箱不能发送form标签，也被过滤了
        结果，很多时候，用户验证需要复制验证连接到浏览器地址栏，然后确认，这个时候发送的是get请求
    '''
    params = request.GET
    errors = []
    if params.has_key('login_id') and params.has_key('validate_code'):
        pass #nothing
    else:
        return HttpResponse("非法操作")

    login_id = params['login_id']
    perishable_token = params['validate_code'].strip()
    user = get_user_by_login_id(login_id)
    if not user:
        return HttpResponse('非法验证')

    if user.status > Status_Passive:
        return HttpResponse('已经验证过了，请直接登录')

    if user.perishable_token != perishable_token:
        return HttpResponse('非法验证')

    user.status = Status_Pending
    user.perishable_token = gene_random_code()
    user.save()

    return HttpResponse('验证成功')

def go_reset_password_by_email(request):
    return render_to_response('go_reset_password_by_email.html', {})

def send_reset_password_email(request):
    '''
    用例：
    用户： 填入email | 验证码待选
    服务器：发送email，用户需要点击这个email才能到重置密码页面；这样可以防止非法访问
    '''
    params = request.POST
    errors = []
    infos = []
    return_hash = {'success':False, 'error':errors, 'user_token':'', 'info': infos}

    validate_email(params, errors, is_must=True)
    if len(errors) > 0 : return HttpResponse(json.dumps(return_hash, ensure_ascii=False))

    login_id = params['email']
    user = get_user_by_email(params['email'])
    if not user:
        errors.append("非法访问")
        return HttpResponse(json.dumps(return_hash, ensure_ascii=False))

    confirm_url = "%s/go_reset_password?login_id=%s&validate_code=%s" % (SITE_FRONT_HOME, login_id, user.perishable_token)
    t = get_template('send_reset_password_email.html')
    html = t.render(Context({'confirm_url': confirm_url, 'user': user, 'login_id': login_id}))
    send_email(user.email, "Push800密码重置邮件", html)

    return_hash['success'] = True
    infos.append("重置链接已经发送到您的邮箱，请登录后点击连接，完成重置密码操作")
    return HttpResponse(json.dumps(return_hash, ensure_ascii=False))

def go_reset_password(request):
    """
    用例描述：用户从邮箱中点击连接，经过验证，合法才能到达重置密码页面
    注意：这个是个web页面；与手机没有关系了
    """
    params = request.GET
    errors = []
    if params.has_key('login_id') and params.has_key('validate_code'):
        pass #nothing
    else:
        return HttpResponse("非法操作")

    login_id = params['login_id']
    perishable_token = params['validate_code'].strip()
    user = get_user_by_login_id(login_id)
    if not user:
        return HttpResponse('非法操作')

    if not user.password_to_reset:
        return HttpResponse('非法操作')

    if not key_exist(params, 'debug'):
        if user.perishable_token != perishable_token:
            return HttpResponse('非法操作')

    return render_to_response("reset_password_by_email.html", {"validate_code":user.perishable_token, "email":user.email})

def reset_password_by_email(request):
    '''
    用户重设密码
    用例描述：
    用户：
        用户填入email，密码，确认密码，点击提交
    服务器：
        验证email格式 | 密码格式
    '''
    params = request.POST
    errors = []
    return_hash = {'error':errors}

    validate_email(params, errors, is_must=True)
    validate_password_and_confirm_password(params, errors, is_must=True)
    if len(errors) > 0: return HttpResponse(json.dumps(return_hash, ensure_ascii=False))

    user = get_user_by_email(params['email'])
    if not user:
        errors.append("非法请求")
        return HttpResponse(json.dumps(return_hash, ensure_ascii=False))

    hashed_password = encrypt_password(params['password'], user.password_salt)
    user.hashed_password = hashed_password
    user.perishable_token = gene_random_code()
    user.save()
    return HttpResponse("您的密码已经重置成功！")

def go_modify_password(request):
    return render_to_response("modify_password.html", {})

def modify_password(request):
    """
    用例描述：
    用户：
        点击“重设秘密”的按钮，进入“修改密码”页面；
        输入密码两次
        提交：提交了当前登录的用户的login_id，应该是email最好了 | 当前的user_code | 两次密码
    服务器：
        验证两次密码 | login_id | user_code
        如果lgoin_id和user_code一致 + login_id一致 => 修改密码+返回成功
    """
    params = request.POST
    errors = []
    return_hash = {'success':False, 'error':errors, 'user_token':''}

    if not key_exist(params, 'password'):
        errors.append("没有填写密码")
        return HttpResponse(json.dumps(return_hash, ensure_ascii=False))

    validate_password_and_confirm_password(params, errors, is_must=True)
    validate_user_token(params, errors)
    if len(errors) > 0: return HttpResponse(json.dumps(return_hash, ensure_ascii=False))

    user = get_user_by_login_id(params['login_id'])
    user.perishable_token = gene_random_code()
    hashed_password = encrypt_password(params['password'], user.password_salt)
    user.hashed_password = hashed_password
    user.save()
    return_hash['success'] = True
    return_hash['user_token'] = user.perishable_token
    return HttpResponse(json.dumps(return_hash, ensure_ascii=False))

#------------------------- 订阅接口 --------------------------#
def subscribes(request):
    """
    获得订阅任务的列表
    """
    ###>>>user check
    params = request.GET
    errors = []
    return_hash = {'success':False, 'error':errors, 'user_token':'', "subscription_list":[]}
    user = get_user(params,errors)
    if not user:
        errors = ["非法访问"]
        return common_return(return_hash)

    ###>>>check params must
    if not key_exist(params, 'business_id'): errors.append("必须填写业务ID")
    if len(errors) > 0: return common_return(return_hash)

    subscription_list = Photograph_Subscribe.objects.filter(user_id=user.id)
    return_hash["subscription_list"] = subscription_list_to_hash(subscription_list)
    return_hash["success"] = True
    return common_return(return_hash)

def add_subscribe(request,city_name):
    '''
    添加订阅
    本来要提供user_token的，2012.02.03改成不需要user_token
    '''
    #可能有查询字段brand_id和keyword，如果是手机会把手机号码和ime也post上来
    brand_id=int(request.POST['brand_id']) if request.POST.has_key('brand_id') and request.POST['brand_id'].isdigit() else 0
    keyword=urllib.unquote_plus(request.POST['keyword'].replace('%20','+')) if request.POST.has_key('keyword') else ''
    if keyword=='': keyword=utils.key_hint
    city_id=int(request.POST['city_id']) if request.POST.has_key('city_id') and request.POST['city_id'].isdigit() else 0
    phone_number=int(request.POST['phone_number']) if request.POST.has_key('phone_number') and request.POST['phone_number'].isdigit() else 0
    phone_ime=request.POST['phone_ime'] if request.POST.has_key('phone_ime')  else ''
    min_price=int(request.POST['min_price']) if request.POST.has_key('min_price') and request.POST['min_price'].isdigit() else 0
    max_price=int(request.POST['max_price']) if request.POST.has_key('max_price') and request.POST['max_price'].isdigit() else 0

    city=utils.get_city(city_id)
    if city is None:
        city=City()
        city.id=0
        city.name_cn=''
        city.name_ab=''

    user=None
    if phone_number==0:
        user=None
    else:
        user=utils.get_user_by_phonenumber(phone_number)
    if user is None:
        user=User()
        user.email=''

    #品牌列表
    brand_list=Photograph_Brand.objects.all()
    district_list=City_District.objects.filter(city=city.id)
    city_list=City.objects.filter(id__lt=6)
    return render_to_response('add_subscribe.html', {'city':city,'city_list':city_list,
                'user':user,'phone_number':phone_number,'phone_ime':phone_ime,'min_price':min_price,
                'max_price':max_price,
                'brand_id':brand_id,'keyword':keyword,'brand_list':brand_list,'district_list':district_list})
    
def create_subscribe(request):
    '''
    提交用户订阅的任务
    注意要夹带business_id方便以后对此接口做扩展,摄影器材的business_id==1
    '''
    #去掉user_token的检查
    params = request.POST
    errors = []
    return_hash = {'success':False, 'error':errors, 'user_token':''}
#    user = get_user(params,errors)
#    if not user:
#        errors.append("非法访问")
#        return common_return(return_hash)

    #check params must
    if not key_exist(params, 'city_id'): errors.append("必须填写城市")
    if not key_exist(params, 'business_id'): errors.append("必须填写业务ID")
    if len(errors) > 0: return common_return(return_hash)

    business_id=int(params['business_id']) if params.has_key('business_id') and params['business_id'].isdigit() else 0

    #business_id==1意味是Photograph_Subscribe
    if business_id==1:
        brand_id=int(request.POST['brand_id']) if request.POST.has_key('brand_id') and request.POST['brand_id'].isdigit() else 0
        keyword=urllib.unquote_plus(request.POST['keyword'].replace('%20','+')) if request.POST.has_key('keyword') else ''
        city_id=int(request.POST['city_id']) if request.POST.has_key('city_id') and request.POST['city_id'].isdigit() else 0
        district_id=int(request.POST['district_id']) if request.POST.has_key('district_id') and request.POST['district_id'].isdigit() else 0
        min_price=int(request.POST['min_price']) if request.POST.has_key('min_price') and request.POST['min_price'].isdigit() else 0
        max_price=int(request.POST['max_price']) if request.POST.has_key('max_price') and request.POST['max_price'].isdigit() else 0
        phone_number=int(request.POST['phone_number']) if request.POST.has_key('phone_number') and request.POST['phone_number'].isdigit() else 0
        phone_ime=unicode(request.POST['phone_ime']) if request.POST.has_key('phone_ime')  else u''
        email=unicode(request.POST['email']) if request.POST.has_key('email')  else u''

        #查询user，如果存在此用户则直接添加，不存在则自动注册新用户
        user=None
        if phone_number>0:
            user=utils.get_user_by_phonenumber(phone_number)
        else:
            user=utils.get_user_by_email(email)
        if user is None:#没有此用户,自动添加此用户
            password_salt = gene_random_code()
            perishable_token = gene_random_code()
            hashed_password = encrypt_password(phone_number, password_salt)
            user = User()
            user.username = phone_number
            user.hashed_password = hashed_password
            user.password_salt = password_salt
            user.perishable_token = perishable_token
            user.register_time = datetime.datetime.now()
            user.email = email
            user.phone_number = phone_number
            user.phone_ime = phone_ime
            user.status = 0
            user.city_id = city_id
            user.district_id = district_id
            if not send_register_validate_email(user):
                errors.append("验证邮件发送失败")
                return HttpResponse(json.dumps(return_hash, ensure_ascii=False))
            user.save()

        subscription = Photograph_Subscribe()
        subscription.user_id = user.id
        subscription.city_id = city_id
        subscription.district_id = district_id
        subscription.brand_id = brand_id
        subscription.min_price = min_price
        subscription.max_price = max_price
        subscription.keyword = keyword
        subscription.email = email
        subscription.created_at = datetime.datetime.now()
        subscription.updated_at = datetime.datetime.now()
        subscription.notify_count = 0
        subscription.status = 1 #valide
        subscription.save()
    elif business_id==2:
        #将来扩展其他业务
        pass

    errors = []
    return_hash['success'] = True
    city=utils.get_city(city_id)
    return render_to_response('subscribe_response.html', {'city':city})

def edit_subscribe(request):
    """
    编辑订阅
    """
    params = request.GET
    errors = []
    return_hash = {'success':False, 'error':errors, 'user_token':''}
    user = get_user(params,errors)
    if not user:
        errors = ["非法访问"]
        return common_return(return_hash)

    if not key_exist(params, 'subscribe_id'):
        errors.append("参数缺失：订阅ID")
        return common_return(return_hash)

    subscribe_id = params['subscribe_id']
    subscription = Photograph_Subscribe.objects.get(id=subscribe_id)
    if not subscription:
        errors.append("订阅不存在")
        return common_return(return_hash)
    
    return render_to_response("edit_subscribe.html", {"user": user, "sub": subscription})

def update_subscribe(request):
    '''
    对订阅任务进行修改
    '''
    ###>>>user check
    params = request.POST
    errors = []
    return_hash = {'success':False, 'error':errors, 'user_token':''}
    user = get_user(params,errors)
    if not user:
        errors = ["非法访问"]
        return common_return(return_hash)

    ###>>>subscribe exist check
    if not key_exist(params, 'subscribe_id'):
        errors.append("参数缺失：订阅ID")
        return common_return(return_hash)

    subscribe_id = params['subscribe_id']
    subscription = Photograph_Subscribe.objects.get(id=subscribe_id)
    if not subscription:
        errors.append("订阅不存在")
        return common_return(return_hash)

    ###>>>params check
    #check params must
    if not key_exist(params, 'city_id'): errors.append("必须填写城市")
    if not key_exist(params, 'business_id'): errors.append("必须填写业务ID")
    if len(errors) > 0: return common_return(return_hash)

    ###>>>params setting
    # subscription = Photograph_Subscribe() # for update comment this BUT for create it not that
    if int(params['business_id'])==1:#business_id==1意味是Photograph_Subscribe
        subscription.user_id = user.id
        subscription.city_id = params['city_id']
        if key_exist(params, 'district_id'): subscription.district_id = params['district_id']
        if key_exist(params, 'brand_id'): subscription.brand_id = params['brand_id']
        if key_exist(params, 'min_price'): subscription.min_price = params['min_price']
        if key_exist(params, 'max_price'): subscription.max_price = params['max_price']
        if key_exist(params, 'keyword'): subscription.keyword = params['keyword']
        #subscription.created_at = datetime.datetime.now() # for update comment this BUT for create it not that
        subscription.updated_at = datetime.datetime.now()
        subscription.notify_count = 0
        subscription.save()
    elif int(params['business_id'])==2:
        #将来扩展其他业务
        pass

    ###>>> common return
    return_hash['success'] = True
    errors = []
    return common_return(return_hash)

def close_subscribe(request):
    '''
    关闭订阅
    '''
    ###>>>user check
    params = request.GET
    errors = []
    return_hash = {'success':False, 'error':errors, 'user_token':''}
    user = get_user(params,errors)
    if not user:
        errors = ["非法访问"]
        return common_return(return_hash)

    ###>>>subscribe exist check
    if not key_exist(params, 'subscribe_id'):
        errors.append("参数缺失：订阅ID")
        return common_return(return_hash)

    subscribe_id = params['subscribe_id']
    subscription = Photograph_Subscribe.objects.get(id=subscribe_id)
    if not subscription:
        errors.append("订阅不存在")
        return common_return(return_hash)

    subscription.status = 0 #closed
    subscription.save()

    return_hash['success'] = True
    return common_return(return_hash)

def destroy_subscribe(request):
    """
    删除订阅
    """
    params = request.GET
    errors = []
    return_hash = {'success':False, 'error':errors, 'user_token':''}
    user = get_user(params,errors)
    if not user:
        errors = ["非法访问"]
        return common_return(return_hash)

    ###>>>user check
    params = request.GET
    errors = []
    return_hash = {'success':False, 'error':errors, 'user_token':''}
    user = get_user(params,errors)
    if not user:
        errors = ["非法访问"]
        return common_return(return_hash)

    ###>>>subscribe exist check
    if not key_exist(params, 'subscribe_id'):
        errors.append("参数缺失：订阅ID")
        return common_return(return_hash)

    subscribe_id = params['subscribe_id']
    subscription = Photograph_Subscribe.objects.get(id=subscribe_id)
    if not subscription:
        errors.append("订阅不存在")
        return common_return(return_hash)

    subscription.delete()
    return_hash['success'] = True
    return common_return(return_hash)

#------------------------- util method --------------------------#
def validate_register_params(params, errors):
    """

    """
    if key_exist(params, 'username'):
        validate_username_format(params['username'], errors)

    validate_email(params, errors, is_must=True)
    validate_password_and_confirm_password(params, errors, is_must=True)

    if key_exist(params, 'phone_number'):
        validate_phone_number_format(params['phone_number'], errors)

    if errors.__len__() > 0: return False #为了减少DB查询次数，这里检查一下

    if username_exist(params['username']):
        errors.append("用户名已经存在")
        return False

    if email_exist(params['email']):
        errors.append("邮箱已经存在")
        return False

    return not errors

def email_exist(email):
    email = email.strip()
    user_list = User.objects.filter(email=email)
    return user_list.__len__() == 1

def username_exist(username):
    username = username.strip()
    user_list = User.objects.filter(username=username)
    return user_list.__len__() == 1

def  key_exist(params, key):
    return params.has_key(key) and params[key].strip().__len__() > 0

def gene_random_code():
    return random.random() + random.randint(0, 9)

def encrypt_password(password, password_salt):
    return "%s_%s" % (password, password_salt)

def validate_username_format(username, errors):
    len_min = 3
    len_max = 24
    if not in_length(username, len_min, len_max):
        errors.append('用户名长度必须符合要求：%s到%s个字符' % (len_min, len_max))

    find = re.search(ur"^[-|\w\u4e00-\u9fa5]+$", username)
    if not find: errors.append('用户名只能是：中文，数字，字母，下划线，减号')
    if re.search(ur"^\d+$", username): errors.append("用户名不能全是数字")

def validate_email_format(email, errors):
    len_min = 6
    len_max = 40
    if not in_length(email, len_min, len_max):
        errors.append('email长度必须符合要求：%s到%s个字符' % (len_min, len_max))

    find = re.search(r"^[\.@\w|-]+$", email)
    if not find:
        errors.append('email必须符合格式，例如：service@push800.com')

def validate_password_format(password, errors):
    len_min = 6
    len_max = 24
    if not in_length(password, len_min, len_max):
        errors.append('密码长度必须符合要求：%s到%s个字符' % (len_min, len_max))

def validate_phone_number_format(phone_number, errors):
    len_min = 11
    len_max = 11
    if not in_length(phone_number, len_min, len_max):
        errors.append('手机号长度必须符合要求：%s个数字' % (len_min))

    find = re.search(r"""^1[\d]+$""", phone_number)
    if not find:
        errors.append('手机号必须符合格式，例如：15101513057')

def validate_email(params, errors, is_must):
    if key_exist(params, 'email'):
        validate_email_format(params['email'], errors)
    else:
        if(is_must): errors.append("邮箱必须填写")

def validate_password_and_confirm_password(params, errors, is_must):
    if key_exist(params, 'password') and key_exist(params, 'confirm_password') and params['password'] == params['confirm_password']:
        validate_password_format(params['password'], errors)
    else:
        if(is_must): errors.append("密码和确认密码必须填写，并且要一致")

def in_length(str, len_min, len_max):
    if not str: return False
    length = str.__len__()
    return length >= len_min and length <= len_max

def get_user_by_login_id(login_id):
    user_list =\
    User.objects.filter(username=login_id) |\
    User.objects.filter(email=login_id)
    if len(user_list) == 1:
        return user_list[0]
    else:
        return None

def get_user_by_email(email):
    user_list = User.objects.filter(email=email)
    if len(user_list) == 1:
        return user_list[0]
    else:
        return None

def is_perishable_token_valid(login_id, token):
    user = get_user_by_login_id(login_id)
    if not user: return False
    return user.perishable_token == token

def send_email(email_address, subject, html):
    m = EmailMessage()
    m.to = email_address
    m.subject = subject
    m.html = html
    m.smtp = ('smtp.sina.com', 25, 'push800@sina.com', 'push800xiaoluo', False)
    return m.send()

def validate_user_token(params, errors):
    if not (key_exist(params, 'login_id') and key_exist(params, 'password')):
        errors.append("非法访问")
        return False
    user = get_user_by_login_id(params['login_id'])
    if not user:
        errors.append("非法访问")
        return False
    if (not params.has_key('user_token')) or (user.perishable_token != params['user_token']):
        errors.append("非法访问")
        return False
    return True
    
def get_user(params, errors):
    if params.has_key('login_id') and params.has_key('user_token'):
        user = get_user_by_login_id(params['login_id'])
        if user and user.perishable_token == params['user_token']:
            return user
    return None
        
def common_return(return_hash):
    return HttpResponse(json.dumps(return_hash, ensure_ascii=False))

def subscription_list_to_hash(subscription_list):
    result = {}
    for subscription in subscription_list:
        result[subscription.id] = subscription_to_hash(subscription)
    return result

def subscription_to_hash(subscription):
    hash = subscription.__dict__
    print "====="
    print hash
    print "====="
    if hash.has_key('_state'): del hash['_state']
    #TODO lijungang. 这里很麻烦啊，得想想怎么处理为好！
    if hash['created_at']: hash['created_at'] = hash['created_at'].strftime('%Y-%M-%d %H:%M:%S')
    if hash['updated_at']: hash['updated_at'] = hash['updated_at'].strftime('%Y-%M-%d %H:%M:%S')
    return hash

    
