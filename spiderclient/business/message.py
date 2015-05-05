#-*- encoding: utf-8 -*-
'''
Created on 2011-7-24

@author: Leo
'''



class Photograph_Message(object):
    '''
    classdocs
    '''
    Seller=''
    Title=''
    Time=''
    Price=''
    Content=''
    Contact=''
    Url=''
    District=''
    Quality=''

    def __init__(self):
        '''
        Constructor
        '''
        self.Seller=''
        self.Title=''
        self.Time=''
        self.Price=''
        self.Content=''
        self.Contact=''
        self.Url=''
        self.City=''
        self.District=''
        self.Quality=''
        
        
    def toString(self):
        print '|| Time='+self.Time
        print '|| Title='+self.Title
        print '|| Quality='+self.Quality
        print '|| Price='+self.Price
        print '|| Url='+self.Url
        print '|| District='+self.District
        print '|| Contact='+self.Contact
        print '|| Content='+self.Content
        
        
