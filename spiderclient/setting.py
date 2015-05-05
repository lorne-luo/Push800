#-*- encoding: utf-8 -*-
'''
常量/设置参数的配置文件

Created on 2011-9-27

@author: Leo
'''
import socket
import re,urllib2,os,sys,uuid

'''线程数'''
THREAD_NUM=5
'''一组任务的数量'''
TASKGROUPNUM=5
'''获取队列超时时间'''
QUEUE_TIMEOUT=5
'''超时时间'''
HTTP_TIMEOUT=60
'''爬行间隔，秒数'''
DEFAULT_SLEEPING_TIME=180
'''爬行次数'''
COUNT=0

'''内部IP，初始化自动获取'''
INTER_IP_ADDRESS=socket.gethostbyname(socket.gethostname())
'''外部IP，初始化自动获取'''
#EXTER_IP_ADDRESS=re.search('\d+\.\d+\.\d+\.\d+',urllib2.urlopen("http://www.whereismyip.com").read()).group(0)
'''爬虫机器名'''
SPIDER_NAME=socket.getfqdn()
'''程序所在目录'''
BASE_PATH=os.path.dirname(os.path.abspath(__file__))+os.sep
'''爬虫module文件夹路径'''
SPIDER_FOLDER='spiders'
'''登陆中央服务器分配的标识'''
TOKEN=''

'''服务器域名'''
BASE_URL='http://push800.sinaapp.com'
#BASE_URL='http://192.168.109.123:8000'
#BASE_URL='http://empty-sunrise-4501.herokuapp.com'
'''spider注册地址'''
SPIDER_LOGIN_URL=BASE_URL+'/spiderserver/spider_login/'
'''获取module列表'''
GET_MODULE_URL=BASE_URL+'/spiderserver/get_modules/'
'''更新module列表'''
UPDATE_MODULE_URL=BASE_URL+'/spiderserver/update_modules/'
'''更新module文件基本地址'''
UPDATE_MODULE_URL=BASE_URL+'/spiderserver/spiders/'
'''获取任务URL'''
GET_TASK_URL=BASE_URL+'/spiderserver/gettasks/'
'''提交任务地址'''
SUBMIT_TASK_URL=BASE_URL+'/spiderserver/submittask/'


class Settings(object):

    def __init__(self, values=None):
        self.values = values.copy() if values else {}
        self.global_defaults = []

    def __getitem__(self, opt_name):
        if opt_name in self.values:
            return self.values[opt_name]
        return getattr(self.global_defaults, opt_name, None)

    def get(self, name, default=None):
        return self[name] if self[name] is not None else default

    def getbool(self, name, default=False):
        """
        True is: 1, '1', True
        False is: 0, '0', False, None
        """
        return bool(int(self.get(name, default)))

    def getint(self, name, default=0):
        return int(self.get(name, default))

    def getfloat(self, name, default=0.0):
        return float(self.get(name, default))

    def getlist(self, name, default=None):
        value = self.get(name)
        if value is None:
            return default or []
        elif hasattr(value, '__iter__'):
            return value
        else:
            return str(value).split(',')

    
'''TEST'''
if __name__ == '__main__':
    print INTER_IP_ADDRESS
    #print EXTER_IP_ADDRESS
    print SPIDER_NAME
    print BASE_PATH
    
    from utils.network import post
    m='{"City": "深圳", "District": "罗湖", "Title": "出让自用佳能数码单反相机一套型号400D", "Url": "http://sz.58.com/shuma/7911275381511x.shtml", "Price": "1980", "Pics": [], "Content": "选项没有400D只有500D勾选。所以别误会。08年山姆会员店买的。当时4600元。自己用到现在。没有拆过，没有修过，完好好用使用中。1980元包含：2个新电池没开封的。2个旧电池都在使用中。1个原厂…", "Contact": "", "Time": "2011-11-21 00:34:42", "Seller": "", "Quality": "70"}'
    print isinstance(m, unicode)
    m = m.encode('utf-8')
    data={'json_str':m}
    echo = post('http://floating-autumn-9293.heroku.com/photograph_messages/create_by_json', data)
    print echo