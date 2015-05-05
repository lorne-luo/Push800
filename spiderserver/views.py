#-*- encoding: utf-8 -*-
from django.http import HttpResponse
import task.spider_manager as sm
import pylibmc
from django.shortcuts import get_object_or_404, render_to_response

def home(request):
    """
    
    """
    d={"user_token": "", "success": False, "error": "四大"}
    import  json
    a=json.dumps(d,ensure_ascii=False)
    b=json.dumps(d)
    return render_to_response('index.html', {'msg_list': ''})