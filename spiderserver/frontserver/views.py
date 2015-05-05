#-*- encoding: utf-8 -*-
# Create your views here.

from models import *
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse
import urllib2,urllib,re

def show_about(request):
    return render_to_response('about.html', {});

def img_proxy(request):
    url=request.GET['url'] if request.GET.has_key('url') else ''

    if url>'':
        req = urllib2.Request(url)
        req.add_header('Referer', get_host(url))
        r = urllib2.urlopen(req)

        response=HttpResponse(r.read())
        response['Content-Type'] = 'image/jpeg'
    else:
        response=HttpResponse('')
    return response

def get_host(url):
    res=''
    m = re.compile('^http://([\d|\w|\.]+)/')
    l=m.match(url)
    if l:
        res=l.group(0)
    return res


'''Test'''
if __name__ == '__main__':
    print get_host('http://ershou.taobao.com/phone_2_image.do?q_p=rO0ABXQACzE4NjE4MzgzNTI3')