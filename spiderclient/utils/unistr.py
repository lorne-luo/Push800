#-*- encoding: utf-8 -*-
"""汉字处理的工具:
判断unicode是否是汉字，数字，英文，或者其他字符。
全角符号转半角符号。"""

__author__ = 'Leo'
__date__="2007-08-04"

def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= u'\u4e00' and uchar<=u'\u9fbb':
        return True
    else:
        return False

def is_number(uchar):
    """判断一个unicode是否是数字"""
    if uchar >= u'\u0030' and uchar<=u'\u0039':
        return True
    else:
        return False

def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    if (uchar >= u'\u0041' and uchar<=u'\u005a') or (uchar >= u'\u0061' and uchar<=u'\u007a'):
        return True
    else:
        return False

def is_other(uchar):
    """判断是否非汉字，数字和英文字符"""
    if not (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar)):
        return True
    else:
        return False

def B2Q(uchar):
    """半角转全角"""
    inside_code=ord(uchar)
    if inside_code<0x0020 or inside_code>0x7e:      #不是半角字符就返回原来的字符
        return uchar
    if inside_code==0x0020: #除了空格其他的全角半角的公式为:半角=全角-0xfee0
        inside_code=0x3000
    else:
        inside_code+=0xfee0
    return unichr(inside_code)

def Q2B(uchar):
    """全角转半角"""
    inside_code=ord(uchar)
    if inside_code==0x3000:
        inside_code=0x0020
    else:
        inside_code-=0xfee0
    if inside_code<0x0020 or inside_code>0x7e:      #转完之后不是半角字符返回原来的字符
        return uchar
    return unichr(inside_code)

def stringQ2B(ustring):
    """把字符串全角转半角"""
    return "".join([Q2B(uchar) for uchar in ustring])

def uniform(ustring):
    """格式化字符串，完成全角转半角，大写转小写的工作"""
    return stringQ2B(ustring).lower()

def string2List(ustring):
    """将ustring按照中文，字母，数字分开"""
    retList=[]
    utmp=[]
    for uchar in ustring:
        if is_other(uchar):
            if len(utmp)==0:
                continue
            else:
                retList.append("".join(utmp))
                utmp=[]
        else:
            utmp.append(uchar)
    if len(utmp)!=0:
        retList.append("".join(utmp))
    return retList


def extract_number(s):
    '''输出字符串中第一个数字，若无返回空'''
    start=0
    lenght=0
    for i in range(len(s)):
        if s[i].isdigit():
            start=i
            for j in range(i,len(s)):
                if s[j].isdigit():
                    lenght+=1
            break
    return s[start:start+lenght]




if __name__=="__main__":
    s=extract_number(u'ddf成新')

    #test Q2B and B2Q
    for i in range(0x0020,0x007F):
        print Q2B(B2Q(unichr(i))),B2Q(unichr(i))

    #test uniform
    ustring=u'中国 人名ａ高频Ａ'
    ustring=stringQ2B(ustring)
    ret=string2List(ustring)
    print ustring

    t=u'ㄟ'
    print unichr(12575)
    print hex(ord(t))
    print hex(ord(u'１'))
    print ord(u'３')

    print is_alphabet(t)

    t=u'服务部咨询电话：１８６=７７７+９９９=３０↗ 可 可 王 经 理一?美?女?上?门?服?务?信?息【１８６ㄟ７７７=９９９ㄟ３０↗ 可 可 王 经 理１８６ㄟ７７７=９９９ㄟ３０↗ 可 可 王 经 理 找?美?女?上?门?包?夜?服?务?信?息【１８６ㄟ７７７=９９９ㄟ３０↗ 可 可 王 经 理１８６ㄟ７７７=９９９ㄟ３０↗ 可 可 王 经 理一?模?特?上?门?全?套?服?务?信?息【１８６ㄟ７７７=９９９ㄟ３０↗ 可 可 王 经 理１８６ㄟ７７７=９９９ㄟ３０↗ 可 可 王 经 理一?学 生 妹?上?门?服?务?信?息【１８６ㄟ７７７=９９９ㄟ３０↗ 可 可 王 经 理--------------------------------------------------?-------------------------------全?套?服?务【１８６ㄟ７７７=９９９ㄟ３０↗ 可 可 王 经 理【１】17?岁?的?中?学?少?女，?乖?巧?玲?珑?可?爱，听?话?配?合，包?吹?包?做《全?套?服?务》【２】大?学?学?生?21?岁，清?纯?阳?光，个?性?开?朗，人?漂?亮．青?春?活?波《全?套?服?务》?【３】成?熟?少?妇，丰?满，服?务?到?位，技?术?好，漂?亮。?《全?套?服?务》?【４】公?司?白?领，皮?肤?好，气?质?好，身?材?好，人?漂?亮，亲?切?爱?笑?热?情?奔?放《全?套?服?务》【５】另?推?极?品?校?花，T?台?模?特：19?岁---23?岁166cm----171cm?上?门?服?务?咨?询?热?线【１８６ㄟ７７７=９９９ㄟ３０↗ 可 可 王 经 理-------------------------------------------------?-------------------------------服 务 部 咨 询:１８６ㄟ７７７=９９９ㄟ３０↗ 可 可 王 经 理 全?套?服?务---- ----------------------------------------- ---?-------------------------------【安?全?问?题】【１８６ㄟ７７７=９９９ㄟ３０↗ 可 可 王 经 理我?们?都?是?上?门?服?务,【１８６ㄟ７７７=９９９ㄟ３０↗ 可 可 王 经 理.比?如?酒?店.宾?馆?等，客?人?觉?得?安?全?方?便?的?地?方.我?们?就?把?人?送?到?什?麽?位?置?的所?以?你?完?全?不?用?担?心?有?什?麽?仙?人?跳?这?些只?有?妹?妹?服?务?好?了.我?们?的?生?意?也?才?能?更?好妹?妹?也?才?能?赚?更?多?的?钱哪?里?有???上?门?服?务--------------------------------------------------?-----------------------------?【上?门?服?务】?【１８６ㄟ７７７=９９９ㄟ３０↗ 可 可 王 经 理主?城?主?要?区?域?都?可?以?上?门?为?你?服?务?的.首?先?需?要?确?认?客?人?的?xx?号?码、地?点.然?后?按?照?客?人?的?要?求?安?排?妹?妹?过?去.如?果?带?来?的?妹?妹?客?人?看?到?不?满?意.你?可?以?直?接?不?要?或?者?换?人?都?可?以.哪?里?有???上?门?服?务?信?息?--------------------------------------------------?-----------------------------【质?量?保?证】【１８６ㄟ７７７=９９９ㄟ３０↗ 可 可 王 经 理我?们?会?根?据?客?人?的?要?求?为?客?人?选?择?最?符?合?客?人?要?求?的?妹?妹.让?司机?把?妹?妹?给?送?到?客?人?指?定?的?位?给?客?人.如果来的?如?果?来?的?妹?妹?您?看?了?不?满?意?的?话.您?可?以?重?新?换.或?者?结?束?服?务.我?们?也?不?会?再?加?收?您?任?何?其?他?的?费?用.?当?然?我?们?做?生?意?的?还?是?不?想?白?跑?所?以?质?量?绝?对?把?关?哪?里?有???上?门?服?务【１８６ㄟ７７７=９９９ㄟ３０↗ 可 可 王 经 理'
    #t=u'服务部咨询电话：１８６=７７７+９９９=３０↗ 可 可 王 经 理'
    t=u'歲?的?中?學?少?女'
    r=0
    for i in xrange(len(t)):
        if 0x9fbb<ord(t[i]) or ord(t[i])<0x4e00:
            #print t[i]
            r+=1
    print r,len(t),float(r)/len(t)
    print is_chinese(u'?')
    print t