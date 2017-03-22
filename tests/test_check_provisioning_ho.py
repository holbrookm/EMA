from __future__ import print_function
import sys
sys.path.insert(0, '/home/ema-gui/emalive')
import ema_functions as ema
import class_ims_ema as ims
import pytest


def test_pro_ho():
    print (" Testing The Hosted Office Provisioning.")
    sub_no = '+353771234567' 
    
    s1 = ims.hostedOfficeSubscriber(sub_no)
    session = {} 
    session['emaSession'] = ema.emaLogin()
    session['sub_pw'] = 'yyeeetteoe'
    result = s1.subscriberCreate(session)
    assert(result.status_code == 200)
    result = s1.subscriberDelete(session)
    assert(result.status_code == 200)

def test_pro_rw():
    print ("Testing Remote Worker Provisioning")
    sub_no = '+353771234567'

    s1 = ims.remoteWorker(sub_no)
    session = {}
    session['emaSession'] = ema.emaLogin()
    session['sub_pw'] = 'yyeeetteoe'
    result = s1.subscriberCreate(session)
    assert(result.status_code == 200)
    result = s1.subscriberDelete(session)
    assert(result.status_code == 200)

def test_pro_non_reg_range():
    print ("Testing Non reg Range Provisioning")
    sub_no = '+3537712346'

    s1 = ims.nonRegisteredRangeSubscriber(sub_no)
    session = {}
    session['rangesize'] = '100'
    session['emaSession'] = ema.emaLogin()
    session['sub_pw'] = 'yyeeetteoe'
    result = s1.subscriberCreate(session)
    assert(result.status_code == 200)
    result = s1.subscriberDelete(session)
    assert(result.status_code == 200)

def test_pro_reg_range():
    print ("Testing  Reg Range Provisioning")

    sub_no = '+3537712346'

    s1 = ims.nonRegisteredRangeSubscriber(sub_no)
    session = {}
    session['rangesize'] = '100'
    session['emaSession'] = ema.emaLogin()
    session['sub_pw'] = 'yyeeetteoe'
    result = s1.subscriberCreate(session)
    assert(result.status_code == 200)
    result = s1.subscriberDelete(session)
    assert(result.status_code == 200)


def test_pro_pilot():
    print ("Testing Pilot Provisioning")
    sub_no = 'PVIMMH17234567'

    s1 = ims.pilotSubscriber(sub_no)
    session = {}
    session['emaSession'] = ema.emaLogin()
    session['sub_pw'] = 'yyeeetteoe'
    result = s1.subscriberCreate(session)
    assert(result.status_code == 200)
    result = s1.subscriberDelete(session)
    assert(result.status_code == 200)


