#!/usr/bin/python

""" This script will access the EMA via http commands with SOAP XML content.
    This will test Ivica's xml for vobb.
    #Marting Remote Worker Provisioning")
    sub_no = '+353771234567'

    s1 = ims.remoteWorker(sub_no)
    session = {}
    session['emaSession'] = ema.emaLogin()
    session['sub_pw'] = 'yyeeetteoe'
    result = s1.subscriberCreate(session)
    assert(result.status_code == 200)
    result = s1.subscriberDelete(session)
    assert(result.status_code == 200) Holbrook
    # 0851742253
    # <mholbrook@eircom.ie>
"""
from __future__ import print_function
import sys
sys.path.insert(0, '/home/ema-gui/emalive')
import ema_functions as ema
import requests
import class_ims_ema as ims
from time import sleep

ema_username= 'sogadm'
ema_password = 'sogadm'
ema_host = '10.147.21.198'  # Live Node
#ema_host = '10.16.6.228'   # Test Plant
ema_port = '8998'
wsdl = 'generic_CAI3G_sessioncontrol.wsdl'

import logging_config
logger = logging_config.logger


def __readinxml__(f):
    ''' Internal method to read in XML file for use within package functions.
    '''
    logger.debug('Method : ema_functions.__readinxml__')

    XML = open(f,'r')
    _xml = XML.read()
    logger.debug('**Leaving FUNC :::: ema_functions.__readinxml__')
    return (_xml)
    
def emaIvicaVOBBSubscriber(session):
    ''' This function will create an IMS subscriber/subscription on HSS and ENUM via EMA.
        The inputs for this subscription are the session 
        and the subscriber information itself.
    '''
    
    insert_xml = __readinxml__('/home/ema-gui/emalive/tests/ivica_vobb_test.xml').format(session['emaSession']['session_id'])
    headers ={'content-type':'text/xml; charset=utf-8', 'SOAPAction':'CAI3G#Create'} 

    print(insert_xml)

    r= requests.post('http://'+session['emaSession']['ema_host'] +':'+ session['emaSession']['ema_port'], data = insert_xml, headers = headers)
    if r.status_code != 200:
        logger.error (' ERROR: An error has occurred trying to create the subscription:::     on the EMA platform.')
        logger.error (r.status_code)
        logger.error (r.text)
    else:
        logger.debug (' Subscription Created !!!!')
        logger.debug (r.text)
    logger.debug('**Leaving FUNC :::: ema_functions.emaCreateRWSubscriber')
    return (r)
    

def emaIvica_rw_set_test(session, sub_no):
    ''' This function will create an IMS subscriber/subscription on HSS and ENUM via EMA.
        The inputs for this subscription are the session
        and the subscriber information itself.
    '''

    insert_xml = __readinxml__('/home/ema-gui/emalive/tests/ivica_rw_sub.xml').format(session['emaSession']['session_id'], sub_no,"@ngv.eircom.net" )
    headers ={'content-type':'text/xml; charset=utf-8', 'SOAPAction':'CAI3G#Create'} 

    logger.debug(insert_xml)

    r= requests.post('http://'+session['emaSession']['ema_host'] +':'+ session['emaSession']['ema_port'], data = insert_xml, headers = headers)
    if r.status_code != 200:
        logger.error ((' ERROR: An error has occurred trying to create the subscription::: {0}    on the EMA platform.').format(sub_no))
        logger.error (r.status_code)
        logger.error (r.text)
    else:
        logger.debug (' Subscription Created !!!!')
        logger.debug (r.text)
    logger.debug('**Leaving FUNC :::: ema_functions.emaCreateImsSubscriber')
    return (r)



session = {} 
session['emaSession'] = ema.emaLogin()
session['sub_pw'] = 'yyeeetteoe'

emaIvicaVOBBSubscriber( session)
print ("##################################################")

print ("Testing Remote Worker Provisioning")
sub_no = '+353771234567'

s1 = ims.remoteWorker(sub_no)
session = {}
session['emaSession'] = ema.emaLogin()
session['sub_pw'] = 'yyeeetteoe'

result = s1.subscriberCreate(session)
print (result)
print (result.text)
sleep (20)
result = emaIvica_rw_set_test(session, sub_no)
print ("##################################################")
print (result)
sleep(30)
print (result.text)
print ("##################################################")

result = s1.subscriberDelete(session)
print (result)

print (result.text)

