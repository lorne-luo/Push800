#-*- encoding: utf-8 -*-
'''
Created on 2012-02-11

@author: Leo
'''
import re,sys
import string

_brands={1:[u'佳能',u'canon'],2:[u'尼康',u'nikon'],3:[u'索尼',u'sony'],4:[u'宾得',u'pentax'],5:[u'富士',u'fuji'],
         6:[u'奥林巴斯',u'olympus',u'奥记'],7:[u'松下','panasonic'],8:[u'理光','ricoh'],9:[u'适马','sigma','shima'],
         10:[u'腾龙','tamron'],11:[u'图丽','tokina'],12:[u'美能达','minolta'],13:[u'哈苏','hasselblad'],
         14:[u'蔡司','zeiss',u'卡尔蔡司',u'卡蔡'],15:[u'徕卡','leica',u'莱卡'],16:[u'柯达','kodak'],17:[u'禄来','rollei'],18:[u'卡西欧','casio'],
         19:[u'康泰时','contax'],20:[u'爱普生','epson'],21:[u'惠普','hp'],22:[u'玛米亚','mamiya'],
         23:[u'柯尼卡','konica'],24:[u'三洋','sanyo'],25:[u'雅西卡','yashica'],26:[u'其他品牌','other'],
         27:[u'三脚架','tripod'],28:[u'摄影包','bag'],29:[u'其它配件','bag'],}

def extract_brand(s):
    s=s.lower()
    for k,v in _brands.iteritems():
        for b in v:
            if s.find(b)>-1:
                return k
    return 29

if __name__=='__main__':
    s=u'自用97新尼康17-55 2.8G 7800不接刀带UV'
    print s.find(' ')
    print extract_brand(s)

