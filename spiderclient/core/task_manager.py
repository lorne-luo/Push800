#-*- encoding: utf-8 -*-

import datetime

_fixtask={}
_randomtask=[]
_task_token=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_fixtask():
    global _fixtask
    return _fixtask

def set_fixtask(data):
    global _fixtask
    global _task_token
    for t in data['task_list']:
        _fixtask[t['id']]=t
    print _fixtask
    _task_token=data['task_token']
    
def get_randomtask():
    global _randomtask
    return _randomtask

def get_task_token():
    global _task_token
    return _task_token


#node启动时向server注册    
def spider_login():
    import uuid
    from utils.network import post
    #uid=uuid.uuid5(uuid.NAMESPACE_DNS, setting.SPIDER_NAME)
    node = uuid.getnode()
    
    info={}
    info['macint']=node
    info['machine_name']=setting.SPIDER_NAME
    
    data = {'login_data':json.dumps(info, ensure_ascii=False)}
    resp = post(setting.SPIDER_LOGIN_URL, data)
    
    loginresp=json.loads(resp)
    
    set_fixtask(loginresp['fixtask'])
    if loginresp['success']:
        load_all_module(loginresp['modules'])
        setting.TOKEN=loginresp['token']
        print 'server token = %s'%(loginresp['token'])
    return loginresp['success']
    
if __name__ == '__main__':
    from core.module_manager import *
    import setting
    print 'INTER_IP_ADDRESS=',setting.INTER_IP_ADDRESS
    print 'EXTER_IP_ADDRESS=',setting.EXTER_IP_ADDRESS
    print 'SPIDER_NAME=',setting.SPIDER_NAME
    
    if not spider_login():
        sys.exit(-1)
    