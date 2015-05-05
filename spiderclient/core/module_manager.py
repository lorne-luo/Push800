#-*- encoding: utf-8 -*-
'''
Created on 2011-11-12

@author: Leo
'''
import os,sys,urllib,urllib2,json,urlparse,httplib,time,socket
from pkgutil import iter_modules
import setting
from utils.network import post

spider_modules={}
update_time=time.time()

"""
SpiderManager is the class which locates and manages all website-specific
spiders
"""



def _import_file(filepath):
    abspath = os.path.abspath(filepath)
    dirname, file = os.path.split(abspath)
    fname, fext = os.path.splitext(file)
    if fext != '.py':
        raise ValueError("Not a Python source file: %s" % abspath)
    if dirname:
        sys.path = [dirname] + sys.path
    try:
        module = __import__(fname, {}, {}, [''])
    finally:
        if dirname:
            sys.path.pop(0)
    return module

def walk_modules(path):
    """Loads a module and all its submodules from a the given module path and
    returns them. If *any* module throws an exception while importing, that
    exception is thrown back.
    For example: walk_modules('scrapy.utils')
    """
    mods = []
    mod = __import__(path, {}, {}, [''])
    #mods.append(mod)
    if hasattr(mod, '__path__'):
        for _, subpath, ispkg in iter_modules(mod.__path__):
            fullpath = path + '.' + subpath
            print fullpath
            if ispkg:
                mods += walk_modules(fullpath)
            else:
                submod = __import__(fullpath, {}, {}, [''])
                mods.append(submod)
    return mods

def check_url_exists(url):
    host,path=urlparse.urlsplit(url)[1:3]
    if ':' in host:
        host,port=host.split(':',1)
        try:
            port=int(port)
        except ValueError:
            print 'invalid port number %r' %(port,)
            sys.exit(1) 
    else:
         port=80
    connection=httplib.HTTPConnection(host,port)
    connection.request("HEAD",path)
    resp=connection.getresponse()
    return resp.status

def get_spider(id):
    if spider_modules.has_key(id):
        return spider_modules[id]['class']
    else:
        return None

def get_spider_byname(name):
    for mod in spider_modules.values():
        if mod['class_name']==name:
            return mod['class']
    return None

def clear_all_module():
    while len(spider_modules):
        item=spider_modules.popitem()
        del item
    print 'spider_modules cleared.'


#download module from server
def download_module(module_name):
    file_name=module_name
    try:
        url=setting.UPDATE_MODULE_URL+file_name+'.py'
        status=check_url_exists(url)
        i=url.rfind('/')
        file=url[i+1:]
        if status==404:
            raise Exception(url+" not exist!")
        #urllib.urlretrieve(setting.UPDATEMODULEURL+file_name+'.py',setting.BASEPATH+setting.SPIDERFOLDER+os.sep+file_name+'1.py')
        urllib.urlretrieve(url,setting.BASE_PATH+setting.SPIDER_FOLDER+os.sep+file_name+'1.py')
        return True
    except Exception,e:
        print type(e),str(e)
        print 'update_module error='+setting.UPDATE_MODULE_URL+file_name+'.py'
        return False
    
def reload_all_module(mod):
    for k in spider_modules.keys():
        reload_module(spider_modules[k]['module'])
        
def reload_module(mod):
    if type(mod) is type(os):
        reload(mod)
        print '[%s] v=%s reloaded'%(mod.__name__,mod.__doc__)
        return True
    elif type(mod) is int:
        try:
            reload(spider_modules[mod]['moudle'])
            print '[%s] v=%s reloaded'%(mod.__name__,mod.__doc__)
            return True
        except:
            return False
    else:
        return False


def load_module(module_name,version):
    try:
        submod = __import__(setting.SPIDER_FOLDER+'.'+module_name, {}, {}, [''])
        if version!=int(submod.__doc__):#服务器和本地version不一致，进行更新
            raise
        return submod
    except:
        if download_module(module_name):
            submod = __import__(setting.SPIDER_FOLDER+'.'+module_name, {}, {}, [''])
            if version!=int(submod.__doc__):
                print 'module [%s] update but version conflicted:server=%d file=%s'%(module_name,version,submod.__doc__)
            else:
                print 'module [%s] update version=%s'%(module_name,submod.__doc__)
            return submod
        else:
            return None

def get_module_info():
    l=[]
    for k,v in spider_modules.items():
        l.append([k,v['version']])
    return  l

def load_all_module(data=None):
    mods=[]
    if data==None:
        page = urllib2.urlopen(setting.GET_MODULE_URL)
        data=page.read()
        mods=json.loads(data)
    else:
        mods=data
    
    count=0
    for m in mods:
        try:
            mod=load_module(m['module_name'],m['version'])
            spiderclass=eval('mod.'+m['class_name'])
            spiderclass.version=m['version']
            spiderclass.id=m['parser_id']
            spider_modules[m['parser_id']]={'module_name':m['module_name'],'class_name':m['class_name'],'module':mod,'class':spiderclass,'version':m['version']}
            count+=1
        except:
            print 'import %s.%s failed'%m['module_name'],m['class_name']
            continue
    print 'module load:receive %d , imported %d '%(len(mods),count)
    update_time=time.time()
        
        
def update_all_module():
    page = urllib2.urlopen(setting.GET_MODULE_URL)
    data=page.read()
    mods=json.loads(data)
    
    for m in mods:
        if not spider_modules.has_key(m['parser_id']):
            if download_module(m['module_name']):
                try:
                    mod = __import__(setting.SPIDER_FOLDER+'.'+m['module_name'], {}, {}, [''])
                    spiderclass=eval('mod.'+m['class_name'])
                    spiderclass.version=m['version']
                    spiderclass.id=m['parser_id']
                    if m['version']!=int(mod.__doc__):
                        print 'module [%s] update but version conflicted:server=%d file=%s'%(m['module_name'],m['version'],mod.__doc__)
                    else:
                        print 'module [%s] update but version=%s'%(m['module_name'],mod.__doc__)
                    spider_modules[m['parser_id']]={'module_name':m['module_name'],'class_name':m['class_name'],'module':mod,'class':spiderclass,'version':m['version']}
                except:
                    print 'update module %s failed'%(m['module_name'])
            else:
                print 'download module %s failed'%(m['module_name'])
            
        elif spider_modules.has_key(m['parser_id']) and m['version']!=spider_modules[m['parser_id']]['version']:#新模块
            if download_module(m['module_name']):
                mod=spider_modules[m['parser_id']]['module']
                reload(mod)
                spider_modules[m['parser_id']]['version']=m['version']
                if m['version']!=int(mod.__doc__):
                    print 'module [%s] update but version conflicted:server=%d file=%s'%(m['module_name'],m['version'],mod.__doc__)
                else:
                    print 'module [%s] update but version=%s'%(m['module_name'],mod.__doc__)

def update_module():
    global update_time
    if time.time()-update_time>3600:
        try:
            update_all_module()
            print 'update_all_module done'
            update_time=time.time()
        except Exception,e:
            print 'update_module err=%s'%str(e)

if __name__ == '__main__':
    load_all_module()
    #spider_modules.popitem()
    #print spider_modules
    print get_module_info()
    
    for k in spider_modules.keys():
        print spider_modules[k]['class'].__name__
        #reload(spider_modules[k]['class'])
    
    spider_modules.popitem()
    spider_modules[2]['version']=0
    print get_module_info()
    update_all_module()
    
    #update_module((u'photograph_fengniao_detail', u'Photograph_Fengniao_Detail_ByID'))
    print get_module_info()        
    
    #load_modules()
    #print spider_modules.values()
    #print dir(spider_modules['spiders.photograph_fengniao_list'])
    #reload(spider_modules['spiders.photograph_fengniao_list'])
    #Photograph_Fengniao_List= spider_modules['spiders.photograph_fengniao_list'].Photograph_Fengniao_List
    #s=Photograph_Fengniao_List('FixTask',1,1,1,2,'http://www.fengniao.com/secforum/search.php?bsid=2&stid=2&ptypeid=2&tkey=&sortorder=&daysprune=&sortfield=posttime',**{u'last_post_id': 1280032, u'last_post_time': u'2011-11-05 01:47:00'})
    #print s.parse.__doc__
    '''
    <type 'exceptions.Exception'> http://127.0.0.1:8000/spiderserver/spiders/photogr
    aph_ganji_list.py not exist!
    update_module error=http://127.0.0.1:8000/spiderserver/spiders/photograph_ganji_
    list.py
    download module photograph_ganji_list failed
    <type 'exceptions.Exception'> http://127.0.0.1:8000/spiderserver/spiders/photogr
    aph_58_detail.py not exist!
    update_module error=http://127.0.0.1:8000/spiderserver/spiders/photograph_58_det
    ail.py
    download module photograph_58_detail failed
    update_all_module done
    '''
    