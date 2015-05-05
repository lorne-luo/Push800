#-*- encoding: utf-8 -*-
'''
Created on 2011-11-4

@author: Leo
'''
import logging,sys

# Logging levels
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL
SILENT = CRITICAL + 1

logging.basicConfig(level=logging.DEBUG,
                format='%(levelname)s|%(asctime)s|%(message)s',
                datefmt='%m-%d %H:%M:%S',
                filename='./spiderclient.log',
                filemode='a+')

def info(msg):
    print msg
    #logging.info(msg)
def debug(msg):
    print msg
    logging.debug(msg)
def err(msg):
    print msg
    logging.error(msg)
def warn(msg):
    print msg
    logging.warning(msg)
def critc(msg):
    logging.critical(msg)

