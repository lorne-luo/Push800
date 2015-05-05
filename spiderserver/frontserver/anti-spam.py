#-*- encoding: utf-8 -*-
__author__ = 'Leo'

from models import *
import spiderserver.utils.unistr as uni

def stat_punctuation_percent():
    msgs=Photograph_Message.objects.filter(is_spam=1).order_by('-id')
    for m in msgs:
        if not len(m.content):
            print m.id,'content=null'
            continue
        punlen=uni.punctuation_percent(m.content)
        m.punctuation_percent=round(punlen/float(len(m.content)),4)
        m.content_len = len(m.content)
        #m.save()
        if m.punctuation_percent<0.5:
            print m.id ,m.content_len,punlen,m.punctuation_percent