#-*- encoding: utf-8 -*-
'''
默认常量/设置参数的配置文件
Created on 2011-11-4
@author: Leo
'''


'''线程数'''
THREADNUM=5
'''超时时间'''
TIMEOUT=15
'''爬行间隔，秒数'''
INTERVAL=300
'''爬行次数'''
COUNT=0

'''内部IP，初始化自动获取'''
INTERIPADDRESS=''
'''外部IP，初始化自动获取'''
EXTERIPADDRESS=''
'''爬虫机器名'''
SPIDERNAME='name'

'''获取任务URL'''
GETTASKURL='http://192.168.109.123:8000/spiderserver/gettasks/'
'''提交任务地址'''
TASKSUBMITURL='http://192.168.109.123:8000/spiderserver/submittask/'