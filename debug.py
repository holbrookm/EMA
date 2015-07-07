#!/usr/bin/python/
import time


global  F_DEBUG
F_DEBUG = 1

def sleep(stringarg):
    if F_DEBUG:
        time.sleep(stringarg)
        pass


def p(stringarg):
    if F_DEBUG:
        print stringarg
        pass

def getflag(): return F_DEBUG

def mac(): return TRUE
    
