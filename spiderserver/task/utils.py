'''
Created on 2011-10-1

@author: Leo
'''
import urllib,urllib2

def post(url, data):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1','Referer':url}
    req = urllib2.Request(url=url,headers = headers)
    data = urllib.urlencode(data)
    #enable cookie
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    response = opener.open(req, data)
    return response.read()

def dict2param(d):
    r=''
    if type(d) is dict:
        for k,v in d.items():
            if not type(k) is str:
                continue
            typev=type(v)
            if typev is str:
                r+=k+r"='"+v+"',"
            elif  typev is int or typev is float:
                r+=k+"="+str(v)+","
    return r[:len(r)-1]
        

        
'''Test'''
if __name__ == '__main__':
    d={'sdg': '123','assdg':123,'asdg':123.3}
    s=dict2param(d)
    print s
    
    
    try:
        posturl = 'http://127.0.0.1:8000/spiderserver/submittask/'
        data = {'result':'myemail'}
        print post(posturl, data)
    except Exception,e:
        print e
