#!/usr/bin/python

""" This script will access the EMA via http commands with SOAP XML content.
    #Marc Holbrook
    # 0851742253
    # <mholbrook@eircom.ie>

    Modified 15-9-16: Added Get DNS Function
    Modified 15/2/17: Added Modify Password Function

"""


import requests, debug
import logging_config
from xml.etree import ElementTree as ET
import xmltodict




ema_username= 'sogadm'
ema_password = 'sogadm'
#ema_host = '10.147.21.198'  # Live Node
ema_host = '10.16.6.228'   # Test Plant
ema_port = '8998'
wsdl = 'generic_CAI3G_sessioncontrol.wsdl'

logger = logging_config.logger

def __readinxml__(f):
    ''' Internal method to read in XML file for use within package functions.
    '''
    logger.debug('Method : ema_functions.__readinxml__')

    XML = open(f,'r')
    _xml = XML.read()
    logger.debug('**Leaving FUNC :::: ema_functions.__readinxml__')
    return (_xml)


def prepareXmlToClass(s):
    """ This function will take an XML string as an input, parse, modify and return a dict 
        ready to be used to create an IMS subscriber Class instance.
    """
    logger.debug("FUNC: prepareXmlToClass     :  ")
    d1 = xmltodict.parse(s)
    d2 = d1['S:Envelope']['S:Body']['GetResponse']['MOAttributes']['getResponseIMSSubscription']
    logger.debug('**Leaving FUNC :::: ema_functions.prepareXmlToClass')
    return d2

def emaLogin(username = 'Marc', password='Marc'):
    ''' This function will login into the EMA platform using the user name and password supplied.'''
    logger.debug(" FUNC: ema_function.emaLogin(Username, Password)       : ")
    insert_xml = __readinxml__('/home/ema-gui/emalive/XML/login.xml')
    sequence_id = ''
    session_id = ''
    return_code = None
    insert_xml = insert_xml.format(ema_username, ema_password)
    logger.debug(insert_xml)
    headers ={'content-type':'text/xml; charset=utf-8','content-length':'503',  'SOAPAction':'CAI3G#Login'}
    r= requests.post('http://'+ema_host +':'+ ema_port, data = insert_xml, headers = headers, auth =(ema_username, ema_password))
    if r.status_code != 200:
        logger.error (' ERROR: An error has occurred trying to login into the EMA platform.')
        logger.error (r.status_code)
        logger.error (r.text)
    else:
        tree= ET.fromstring(r.text)
        for node in tree.getiterator():
            if node.tag == '{http://schemas.ericsson.com/cai3g1.2/}baseSequenceId': sequence_id = node.text
            if node.tag == '{http://schemas.ericsson.com/cai3g1.2/}sessionId' : session_id = node.text
        if sequence_id !='' and session_id !='':
            logger.debug  (('Sequence Id 1 :   {0}    ::::: Session Id 1 :   {1}').format (sequence_id, session_id))
            session = { "sequence_id" : sequence_id, "session_id": session_id, "transaction_id" : "12334455", "ema_host": ema_host, "ema_port": ema_port}
            return_code = (session)
    logger.debug('**Leaving FUNC :::: ema_functions.emaLogin')
    return (return_code) # Return login information for future requests

def ema_logout(session_id):
    ''' This function will logout of the EMA platform using the session id supplied.'''
    logger.debug(" FUNC: ema_logut   : ")
    XML = open('/home/ema-gui/emalive/XML/ema_logout.xml','r')
    insert_xml = XML.read().format(session_id)
    logger.debug(insert_xml)
    headers ={'content-type':'text/xml; charset=utf-8',  'SOAPAction':'CAI3G#Logout'}
    r= requests.post('http://'+ema_host +':'+ ema_port, data = insert_xml, headers = headers, auth =('sogadm', 'sogadm'))
    if r.status_code != 200:
        logger.error (' ERROR: An error has occurred trying to logout of the EMA platform.')
        logger.error (r.status_code)
        logger.error (r.text)
    else:
        logger.debug (' Logout successfull!!!!')
        logger.debug (r.text)
    logger.debug('**Leaving FUNC :::: ema_functions.ema_logout')
    return


def emaGetImsSubscriber(sub, session):
    ''' This function will search EMA for a specified IMS subscription and retrieve subscription information.
        This function takes a subscriberId as input and returns the subscription xml.
        The sequenceId, transaction_id and sessionId must alos be supplied.
        This function returns an XML string of Subscriber Information or Error Information.
    '''
    debug.p ('Func::: emaGetImsSuscriber (sub, session)     : ')
    logger.debug('Func::: emaGetImsSuscriber (sub, session)     : ')

    insert_xml = __readinxml__('/home/ema-gui/emalive/XML/get_ims_sub.xml').format(session['emaSession']['sequence_id'], session['emaSession']['transaction_id'],session['emaSession']['session_id'], sub.subscriberId)
    logger.debug(insert_xml)
    
    headers ={'content-type':'text/xml; charset=utf-8',  'SOAPAction':'CAI3G#Get'}
    r= requests.post('http://'+session['emaSession']['ema_host'] +':'+ session['emaSession']['ema_port'], data = insert_xml, headers = headers)
    if r.status_code != 200:
        logger.info((' INFO: An error has occurred trying to retrieve the subscription::: {0}    from the EMA platform.').format(sub.subscriberId))
        logger.info (r.status_code)
        logger.info (r.text)
    else:
        logger.debug (' Subscription found!!!!')
        logger.debug (r.text)
    logger.debug('**Leaving FUNC :::: ema_functions.emaGetImsSubscriber')
    debug.p('**Leaving FUNC :::: ema_functions.emaGetImsSubscriber')
    return (r)

def emaCreateImsSubscriber(sub, session):
    ''' This function will create an IMS subscriber/subscription on HSS and ENUM via EMA.
        The inputs for this subscription are the session/sequence/transaction ids 
        and the subscriber information itself.
    '''
    logger.debug('FUNC:: emaCreateImsSubscriber (sub, session)     :   ')

    insert_xml = __readinxml__('/home/ema-gui/emalive/XML/lmi_create_ims_rw_sub_marc.xml').format(session['emaSession']['session_id'], sub.phoneNumber, sub.domain, sub.origProfileId, sub.termProfileId, sub.chargingProfId, sub.password)
    headers ={'content-type':'text/xml; charset=utf-8', 'SOAPAction':'CAI3G#Create'} 

    logger.debug(insert_xml)

    r= requests.post('http://'+session['emaSession']['ema_host'] +':'+ session['emaSession']['ema_port'], data = insert_xml, headers = headers)
    if r.status_code != 200:
        logger.error ((' ERROR: An error has occurred trying to create the subscription::: {0}    on the EMA platform.').format(sub.subscriberId))
        logger.error (r.status_code)
        logger.error (r.text)
    else:
        logger.debug (' Subscription Created !!!!')
        logger.debug (r.text)
    logger.debug('**Leaving FUNC :::: ema_functions.emaCreateImsSubscriber')
    return (r)

    
def emaCreateRWSubscriber(sub, session):
    ''' This function will create an IMS subscriber/subscription on HSS and ENUM via EMA.
        The inputs for this subscription are the session 
        and the subscriber information itself.
    '''
    logger.debug(('FUNC:: emaCreateRWSubscriber  {0}, {1}    :   ').format(sub, session))

    insert_xml = __readinxml__('/home/ema-gui/emalive/XML/lmi_create_ims_rw_sub_marc.xml').format(session['emaSession']['session_id'], sub.phoneNumber, sub.domain, sub.origProfileId, sub.termProfileId, sub.chargingProfId, sub.password)
    headers ={'content-type':'text/xml; charset=utf-8', 'SOAPAction':'CAI3G#Create'} 

    logger.debug(insert_xml)

    r= requests.post('http://'+session['emaSession']['ema_host'] +':'+ session['emaSession']['ema_port'], data = insert_xml, headers = headers)
    if r.status_code != 200:
        logger.error ((' ERROR: An error has occurred trying to create the subscription::: {0}    on the EMA platform.').format(sub.subscriberId))
        logger.error (r.status_code)
        logger.error (r.text)
    else:
        logger.debug (' Subscription Created !!!!')
        logger.debug (r.text)
    logger.debug('**Leaving FUNC :::: ema_functions.emaCreateRWSubscriber')
    return (r)

def emaCreateNonRegisteredRangeSubscriber(sub, session):
    ''' This function will create an IMS subscriber/subscription on HSS and ENUM via EMA.
        The inputs for this subscription are the session 
        and the subscriber information itself.
    '''
    logger.debug(('FUNC:: emaCreateNonRegisteredRangeSubscriber  {0}, {1}    :   ').format(sub, session))
    debug.p(session['rangesize'])

    if session['rangesize'] == '10':
        debug.p('Entering 10')
        insert_xml = __readinxml__('/home/ema-gui/emalive/XML/create_psi_ims_rangeNR_marc.xml').format(session['emaSession']['session_id'], sub.phoneNumber, sub.domain, sub.termProfileId, sub.chargingProfId, '{1}', sub.pubData.publicIdTelValue)
        #insert_xml = __readinxml__('/home/ema-gui/emalive/XML/lmi_create_ims_rangeNR10_marc.xml').format(session['emaSession']['session_id'], sub.phoneNumber, sub.domain, sub.origProfileId, sub.termProfileId, sub.chargingProfId, sub.password)
    elif session['rangesize'] == '100':
        debug.p('Entering 100')
        insert_xml = __readinxml__('/home/ema-gui/emalive/XML/create_psi_ims_rangeNR_marc.xml').format(session['emaSession']['session_id'], sub.phoneNumber, sub.domain, sub.termProfileId, sub.chargingProfId, '{2}', sub.pubData.publicIdTelValue)
    elif session['rangesize'] == '1000':
        debug.p('Entering 1000')
        insert_xml = __readinxml__('/home/ema-gui/emalive/XML/create_psi_ims_rangeNR_marc.xml').format(session['emaSession']['session_id'], sub.phoneNumber, sub.domain, sub.termProfileId, sub.chargingProfId, '{3}', sub.pubData.publicIdTelValue)
    elif session['rangesize'] == '10000':
        debug.p('Entering 10000')
        insert_xml = __readinxml__('/home/ema-gui/emalive/XML/create_psi_ims_rangeNR_marc.xml').format(session['emaSession']['session_id'], sub.phoneNumber, sub.domain, sub.termProfileId, sub.chargingProfId, '{4}', sub.pubData.publicIdTelValue)  
    else:
        pass # go to error
    headers ={'content-type':'text/xml; charset=utf-8', 'SOAPAction':'CAI3G#Create'} 

    logger.debug(insert_xml)

    r= requests.post('http://'+session['emaSession']['ema_host'] +':'+ session['emaSession']['ema_port'], data = insert_xml, headers = headers)
    if r.status_code != 200:
        logger.error ((' ERROR: An error has occurred trying to create the subscription::: {0}    on the EMA platform.').format(sub.subscriberId))
        logger.error (r.status_code)
        logger.error (r.text)
    else:
        logger.debug (' Subscription Created !!!!')
        logger.debug (r.text)
    logger.debug('**Leaving FUNC :::: ema_functions.emaCreateNonRegisteredRangeSubscriber')
    return (r) 
 
def emaCreateRegisteredRangeSubscriber(sub, session):
    ''' This function will create an IMS subscriber/subscription on HSS and ENUM via EMA.
        The inputs for this subscription are the session 
        and the subscriber information itself.
    '''
    logger.debug(('FUNC:: emaCreateRegisteredRangeSubscriber  {0}, {1}    :   ').format(sub, session))
    debug.p(session['rangesize'])

    if session['rangesize'] == '10':
        debug.p('Entering 10')
        insert_xml = __readinxml__('/home/ema-gui/emalive/XML/create_psi_ims_rangeNR_marc.xml').format(session['emaSession']['session_id'], sub.phoneNumber, sub.domain, sub.termProfileId, sub.chargingProfId, '{1}', sub.pubData.publicIdTelValue)
        #insert_xml = __readinxml__('/home/ema-gui/emalive/XML/lmi_create_ims_rangeNR10_marc.xml').format(session['emaSession']['session_id'], sub.phoneNumber, sub.domain, sub.origProfileId, sub.termProfileId, sub.chargingProfId, sub.password)
    elif session['rangesize'] == '100':
        debug.p('Entering 100')
        insert_xml = __readinxml__('/home/ema-gui/emalive/XML/create_psi_ims_rangeNR_marc.xml').format(session['emaSession']['session_id'], sub.phoneNumber, sub.domain, sub.termProfileId, sub.chargingProfId, '{2}', sub.pubData.publicIdTelValue)
    elif session['rangesize'] == '1000':
        debug.p('Entering 1000')
        insert_xml = __readinxml__('/home/ema-gui/emalive/XML/create_psi_ims_rangeNR_marc.xml').format(session['emaSession']['session_id'], sub.phoneNumber, sub.domain, sub.termProfileId, sub.chargingProfId, '{3}', sub.pubData.publicIdTelValue)
    elif session['rangesize'] == '10000':
        debug.p('Entering 10000')
        insert_xml = __readinxml__('/home/ema-gui/emalive/XML/create_psi_ims_rangeNR_marc.xml').format(session['emaSession']['session_id'], sub.phoneNumber, sub.domain, sub.termProfileId, sub.chargingProfId, '{4}', sub.pubData.publicIdTelValue)  
    else:
        pass # go to error
    headers ={'content-type':'text/xml; charset=utf-8', 'SOAPAction':'CAI3G#Create'} 

    logger.debug(insert_xml)

    r= requests.post('http://'+session['emaSession']['ema_host'] +':'+ session['emaSession']['ema_port'], data = insert_xml, headers = headers)
    if r.status_code != 200:
        logger.error ((' ERROR: An error has occurred trying to create the subscription::: {0}    on the EMA platform.').format(sub.subscriberId))
        logger.error (r.status_code)
        logger.error (r.text)
    else:
        logger.debug (' Subscription Created !!!!')
        logger.debug (r.text)
    logger.debug('**Leaving FUNC :::: ema_functions.emaCreateRegisteredRangeSubscriber')
    return (r) 
 
 
def emaCreateRegisteredPBXPilotNumber(sub, session):
    ''' This function will create an IMS subscriber/subscription on HSS and ENUM via EMA.
        The inputs for this subscription are the session 
        and the subscriber information itself.
    '''
    logger.debug(('FUNC:: emaCreateRegisteredPBXPilotNumber  {0}, {1}    :   ').format(sub, session))

    insert_xml = __readinxml__('/home/ema-gui/emalive/XML/lmi_create_ims_reg_pbx_pilot_marc.xml').format(session['emaSession']['session_id'], sub.phoneNumber, sub.domain, sub.origProfileId, sub.password)
    headers ={'content-type':'text/xml; charset=utf-8', 'SOAPAction':'CAI3G#Create'} 

    logger.debug(insert_xml)

    r= requests.post('http://'+session['emaSession']['ema_host'] +':'+ session['emaSession']['ema_port'], data = insert_xml, headers = headers)
    if r.status_code != 200:
        logger.error ((' ERROR: An error has occurred trying to create the subscription::: {0}    on the EMA platform.').format(sub.subscriberId))
        logger.error (r.status_code)
        logger.error (r.text)
    else:
        logger.debug (' Subscription Created !!!!')
        logger.debug (r.text)
    logger.debug('**Leaving FUNC :::: ema_functions.emaCreateRegisteredPBXPilotNumber')
    return (r)
    
def emaCreateHOSubscriber(sub, session):
    ''' This function will create an IMS subscriber/subscription on HSS and ENUM via EMA.
        The inputs for this subscription are the session/sequence/transaction ids 
        and the subscriber information itself.
    '''
    logger.debug(('FUNC:: emaCreateHOSubscriber    {0}, {1}  :   ').format(sub, session))

   
    insert_xml = __readinxml__('/home/ema-gui/emalive/XML/create_hostedoffice_subscriber_lmi.xml').format(session['emaSession']['session_id'], sub.phoneNumber, sub.domain, sub.origProfileId, sub.termProfileId, session['sub_pw'],sub.pubData.phoneContext)    
    #insert_xml = __readinxml__('/home/ema-gui/emalive/XML/create_hostedoffice_subscriber.xml').format(session['emaSession']['sequence_id'], session['emaSession']['transaction_id'],session['emaSession']['session_id'], sub.subscriberId, sub.msisdn, sub.pubData.publicIdValue, sub.pubData.publicIdTelValue, sub.pubData.phoneContext, sub.pubData.privateUserId, sub.origProfileId, sub.termProfileId, sub.chargingProfId, session['ho_pw'])
    
    headers ={'content-type':'text/xml; charset=utf-8', 'SOAPAction':'CAI3G#Create'} 

    logger.debug(insert_xml)

    r= requests.post('http://'+ session['emaSession']['ema_host'] +':'+ session['emaSession']['ema_port'], data = insert_xml, headers = headers)
    if r.status_code != 200:
        logger.error ((' ERROR: An error has occurred trying to create the subscription::: {0}    on the EMA platform.').format(sub.subscriberId))
        logger.error (r.status_code)
        logger.error (r.text)
    else:
        logger.debug (' Subscription Created !!!!')
        logger.debug (r.text)
    logger.debug('**Leaving FUNC :::: ema_functions.emaCreateImsSubscriber')
    return (r)

def emaDeleteImsSubscriber(subscriber,session):
    ''' This function will create an IMS subscriber/subscription on HSS and ENUM via EMA.
        The inputs for this subscription are the session/sequence/transaction ids 
        and the subscriber (class instance)information itself.
    '''
    logger.debug(('FUNC:: emaDeleteImsSubscriber   {0}, {1}   :   ').format(subscriber, session))

    insert_xml = __readinxml__('/home/ema-gui/emalive/XML/delete_ims_subscriber.xml').format(session['emaSession']['sequence_id'], session['emaSession']['transaction_id'],session['emaSession']['session_id'], subscriber.subscriberId)
    headers ={'content-type':'text/xml; charset=utf-8', 'SOAPAction':'CAI3G#Delete'} 

    logger.debug(insert_xml)

    r= requests.post('http://'+session['emaSession']['ema_host'] +':'+ session['emaSession']['ema_port'], data = insert_xml, headers = headers)
    if r.status_code != 200:
        logger.error ((' ERROR: An error has occurred trying to delete the subscription::: {0}    on the EMA platform.').format(subscriber.subscriberId))
        logger.error (r.status_code)
        logger.error (r.text)
    else:
        logger.debug (' Subscription Deleted !!!!')
        logger.debug (r.text)
    logger.debug('**Leaving FUNC :::: ema_functions.emaDeleteImsSubscriber')
    return (r)


def emaCreateVobbSubscriber(session, msisdn, subscriberId, publicId, domain, password):
    ''' This function should create a VOBB retail subscription via EMA and return the results.

    '''
    logger.debug(('FUNC:: ema_functions.emaCreateVobbSubscriber  {0}  :   ').format(subscriberId))
    insert_xml = __readinxml__('/home/ema-gui/emalive/XML/create_vobb_ims_subscriber1.xml').format(session['emaSession']['session_id'], msisdn, subscriberId, publicId, domain, password)
    headers ={'content-type':'text/xml; charset=utf-8', 'SOAPAction':'CAI3G#Create'}

    logger.debug(insert_xml)
    r = requests.post('http://'+ session['emaSession']['ema_host'] +':'+ session['emaSession']['ema_port'], data = insert_xml, headers = headers)
    if r.status_code != 200:
        logger.error ((' ERROR: An error has occurred trying to retrieve the DNS Entry ::: {0}    on the EMA platform.').format(subscriberId))
        logger.error (r.status_code)
        logger.error (r.text)
    else:
        logger.debug (' Subscriber created !!!!')
        logger.debug (r.text)
    
    logger.debug(' **Leaving FUNC :::: ema_functions.emaCreateVobbSubscriber')
    return (r)

def emaDeleteVobbSubscriber(session, msisdn, domain):
    ''' This function should create a VOBB retail subscription via EMA and return the results.

    '''
    logger.debug(('FUNC:: ema_functions.emaDeleteVobbSubscriber  {0}  :   ').format(msisdn))
    insert_xml = __readinxml__('/home/ema-gui/emalive/XML/delete_vobb_ims_subscriber.xml').format(session['emaSession']['session_id'], msisdn, domain)
    headers ={'content-type':'text/xml; charset=utf-8', 'SOAPAction':'CAI3G#Delete'}

    logger.debug(insert_xml)
    r = requests.post('http://'+ session['emaSession']['ema_host'] +':'+ session['emaSession']['ema_port'], data = insert_xml, headers = headers)
    if r.status_code != 200:
        logger.error ((' ERROR: An error has occurred trying to retrieve the DNS Entry ::: {0}    on the EMA platform.').format(msisdn))
        logger.error (r.status_code)
        logger.error (r.text)
    else:
        logger.debug (' Subscriber Deleted !!!!')
        logger.debug (r.text)

    logger.debug(' **Leaving FUNC :::: ema_functions.emaDeleteVobbSubscriber')
    return (r)

def emaModifyPassword(sub, session):
    ''' This function should create a VOBB retail subscription via EMA and return the results.
        Added 15-2-17.
    '''
    logger.debug(('FUNC:: ema_functions.emaModifyPassword  {0}  :   ').format(sub.subscriberId))
    insert_xml = __readinxml__('/home/ema-gui/emalive/XML/modify_password.xml').format(session['emaSession']['session_id'], sub.subscriberId, sub.password)
    headers ={'content-type':'text/xml; charset=utf-8', 'SOAPAction':'CAI3G#Set'}

    logger.debug(insert_xml)
    r = requests.post('http://'+ session['emaSession']['ema_host'] +':'+ session['emaSession']['ema_port'], data = insert_xml, headers = headers)
    if r.status_code != 200:
        logger.error ((' ERROR: An error has occurred trying to modify the password for ::: {0}    on the EMA platform.').format(sub.subscriberId))
        logger.error (r.status_code)
        logger.error (r.text)
    else:
        logger.debug (' Password Modified !!!!')
        logger.debug (r.text)

    logger.debug(' **Leaving FUNC :::: ema_functions.emaModifyPassword')
    return (r)

def emaGetVobbSubscriber(session, subscriberId):
    ''' This function should create a VOBB retail subscription via EMA and return the results.

    '''
    logger.debug(('FUNC:: ema_functions.emaGetVobbSubscriber  {0}  :   ').format(subscriberId))
    insert_xml = __readinxml__('/home/ema-gui/emalive/XML/get_vobb_ims_subscriber.xml').format(session['emaSession']['session_id'], subscriberId)
    headers ={'content-type':'text/xml; charset=utf-8', 'SOAPAction':'CAI3G#Get'}

    logger.debug(insert_xml)
    r = requests.post('http://'+ session['emaSession']['ema_host'] +':'+ session['emaSession']['ema_port'], data = insert_xml, headers = headers)
    if r.status_code != 200:
        logger.error ((' ERROR: An error has occurred trying to retrieve the DNS Entry ::: {0}    on the EMA platform.').format(subscriberId))
        logger.error (r.status_code)
        logger.error (r.text)
    else:
        logger.debug (' Subscriber Retrieved!!!!')
        logger.debug (r.text)

    logger.debug(' **Leaving FUNC :::: ema_functions.emaDeleteVobbSubscriber')
    return (r)



def emaGetDnsEntry( session, msisdn, subscriberId):
    ''' This function should accept input variable and session id and query EMA for a DNS entry from ssDNS.
        The response should be a valid or incorrect DNS response from EMA.
    '''
    logger.debug(('FUNC:: ema_functions.emaGetDnsEntry  {0}, {1}   :   ').format(subscriberId, session))
    insert_xml = __readinxml__('/home/ema-gui/emalive/XML/get_dns.xml').format(session['emaSession']['session_id'], msisdn, subscriberId)
    headers ={'content-type':'text/xml; charset=utf-8', 'SOAPAction':'CAI3G#Get'}

    logger.debug(insert_xml)

    r = requests.post('http://'+ session['emaSession']['ema_host'] +':'+ session['emaSession']['ema_port'], data = insert_xml, headers = headers)
    if r.status_code != 200:
        logger.error ((' ERROR: An error has occurred trying to retrieve the DNS Entry ::: {0}    on the EMA platform.').format(subscriberId))
        logger.error (r.status_code)
        logger.error (r.text)
    else:
        logger.debug (' DNS Retrieved !!!!')
        logger.debug (r.text)
    
    logger.debug(' **Leaving FUNC :::: ema_functions.emaGetDnsEntry')
    return (r)


def emaCreateSLF(session,subscriberId):
    ''' WARNING: Only use this for negative testing.
        This function should create an SLF entry via EMA and return the results.

    '''
    logger.debug(('FUNC:: ema_functions.emaCreateSLF  {0}  :   ').format(subscriberId))
    insert_xml = __readinxml__('/home/ema-gui/emalive/XML/create_SLF.xml').format(session['emaSession']['session_id'],subscriberId)
    headers ={'content-type':'text/xml; charset=utf-8', 'SOAPAction':'CAI3G#Create'}

    logger.debug(insert_xml)
    r = requests.post('http://'+ session['emaSession']['ema_host'] +':'+ session['emaSession']['ema_port'], data = insert_xml, headers = headers)
    if r.status_code != 200:
        logger.error ((' ERROR: An error has occurred trying to retrieve the DNS Entry ::: {0}    on the EMA platform.').format(subscriberId))
        logger.error (r.status_code)
        logger.error (r.text)
    else:
        logger.debug (' SLF Entry created !!!!')
        logger.debug (r.text)

    logger.debug(' **Leaving FUNC :::: ema_functions.emaCreateSLF')
    return (r)

def emaDeleteSLF(session, subscriberId):
    ''' WARNING: USE ONLY FOR NEGATIVE TESTING
        This function should delete an SLF entry via EMA and return the results.

    '''
    logger.debug(('FUNC:: ema_functions.emaDeleteSLF  {0}  :   ').format(subscriberId))
    insert_xml = __readinxml__('/home/ema-gui/emalive/XML/delete_vobb_ims_subscriber.xml').format(session['emaSession']['session_id'], subscriberId)
    headers ={'content-type':'text/xml; charset=utf-8', 'SOAPAction':'CAI3G#Delete'}

    logger.debug(insert_xml)
    r = requests.post('http://'+ session['emaSession']['ema_host'] +':'+ session['emaSession']['ema_port'], data = insert_xml, headers = headers)
    if r.status_code != 200:
        logger.error ((' ERROR: An error has occurred trying to retrieve the DNS Entry ::: {0}    on the EMA platform.').format(subscriberId))
        logger.error (r.status_code)
        logger.error (r.text)
    else:
        logger.debug (' Subscriber Deleted !!!!')
        logger.debug (r.text)

    logger.debug(' **Leaving FUNC :::: ema_functions.emaDeleteSLF')
    return (r)


def emaGetSLF(session, subscriberId, publicId):
    ''' This function should create a VOBB retail subscription via EMA and return the results.

    '''
    logger.debug(('FUNC:: ema_functions.emaGetSLF  {0}  :   ').format(subscriberId, publicId))
    insert_xml = __readinxml__('/home/ema-gui/emalive/XML/get_vobb_ims_subscriber.xml').format(session['emaSession']['session_id'], subscriberId, publicId)
    headers ={'content-type':'text/xml; charset=utf-8', 'SOAPAction':'CAI3G#Get'}

    logger.debug(insert_xml)
    r = requests.post('http://'+ session['emaSession']['ema_host'] +':'+ session['emaSession']['ema_port'], data = insert_xml, headers = headers)
    if r.status_code != 200:
        logger.error ((' ERROR: An error has occurred trying to retrieve the DNS Entry ::: {0}    on the EMA platform.').format(subscriberId))
        logger.error (r.status_code)
        logger.error (r.text)
    else:
        logger.debug (' Subscriber Retrieved!!!!')
        logger.debug (r.text)

    logger.debug(' **Leaving FUNC :::: ema_functions.emaGetSLF')
    return (r)





if __name__ == "__main__":
    main()




