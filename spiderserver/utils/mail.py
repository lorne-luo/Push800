#-*- encoding: utf-8 -*-
__author__ = 'Leo'

from sae.mail import EmailMessage
from sae.taskqueue import add_task
from django.http import HttpResponse
from spiderserver.frontserver.models import *
import base64,urllib


import sys
reload(sys)
sys.setdefaultencoding('utf8')


def send_single_email(email_address, subject, html):
    '''
    发送单封邮件
    '''
    m = EmailMessage()
    m.to = email_address
    #m.subject = subject.encode('utf-8') if type(subject) is unicode else str(subject)
    #m.html = html.encode('utf-8') if type(html) is unicode else str(html)
    m.subject = unicode(subject)
    m.html = unicode(html)
    m.smtp = ('smtp.sina.com', 25, 'push800@sina.com', 'push800xiaoluo', False)
    return m.send()

def send_email_request(request):
    '''
    发送单封邮件的请求接口
    '''


    email_address=request.POST['email_address'] if request.POST.has_key('email_address') else None
    subject=request.POST['subject'] if request.POST.has_key('subject') else None
    html=request.POST['html'] if request.POST.has_key('html') else None
    #subject=base64.decodestring(subject)
    #html=base64.decodestring(html)

    if email_address!=None:
        #返回==None
        res=send_single_email(email_address, subject, html)
        if res==False:
            trycount=int(request.POST['trycount']) if request.POST.has_key('trycount') else 3
            psm_id=int(request.POST['psm_id']) if request.POST.has_key('psm_id') else 0
            if trycount<3:
                #重试
                trycount+=1
                postdata='email_address=%s&subject=%s&html=&s&psm_id=%d&trycount=%d'%(email_address, subject, html,psm_id,trycount)
                add_task('MailQueue', '/frontserver/send_email_request/', postdata)
                return HttpResponse('RETRY = '+str(trycount))
            else:
                #置psm_id为失败

                return HttpResponse('RETRY=3 SEND FAILED')
        return HttpResponse('SEND RESULT = '+str(res))
    else:
        return HttpResponse('No mail address')

def send_mutil_email(email_list, subject, html,psm_id):
    '''
    发送多封邮件，未来应改成利用sae的taskqueue发送的形式
    '''
    subject = subject.encode('utf-8') if type(subject) is unicode else subject
    html = html.encode('utf-8') if type(html) is unicode else html
    #subject=base64.encodestring(subject)
    #html=base64.encodestring(html)
    for e in email_list:
        #任务初次添加到队列，trycount=0
        postdata={'email_address':e,'subject':subject,'html':html,'psm_id':psm_id,'trycount':0}
        p=urllib.urlencode(postdata)
        add_task('MailQueue', '/frontserver/send_email_request/', p)
    return postdata

def mail_test(request):
    '''测试用'''
    email_list=['1615990@qq.com','24552518@163.com']
    m=Photograph_Message.objects.get(id=189777)
    subject=unicode(m.title)
    html=unicode(m.content)
    html=html.replace(u'\n',u'<br>')
    send_mutil_email(email_list, subject, html,189777)
    return HttpResponse(str(type(subject))+'<br>'+'<br>'+subject+'<br>'+html)