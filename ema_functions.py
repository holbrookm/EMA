#!/usr/bin/python

""" This script will access the EMA via http commands with SOAP XML content.
    #Marc Holbrook
    # 0851742253
    # <mholbrook@eircom.ie>
"""


import os,requests, debug
from prettyprint import pp
from xml.etree import ElementTree as ET
import xmltodict
import class_ims_ema as imsSub


ema_username= 'sogadm'
ema_password = 'sogadm'
ema_host = '10.16.6.228'
ema_port = '8998'
wsdl = 'generic_CAI3G_sessioncontrol.wsdl'

def __readinxml__(f):
    ''' Internal method to read in XML file for use within package functions.
    '''
    debug.p('Method : ema_functions.__readinxml__')

    XML = open(f,'r')
    _xml = XML.read()
    return (_xml)


def prepareXmlToClass(s):
    """ This function will take an XML string as an input, parse, modify and return a dict 
        ready to be used to create an IMS subscriber Class instance.
    """
    debug.p("FUNC: prepareXmlToClass     :  ")
    d1 = xmltodict.parse(s)
    d2 = d1['S:Envelope']['S:Body']['GetResponse']['MOAttributes']['getResponseIMSSubscription']
    return d2

def emaLogin(username = 'Marc', password='Marc'):
    ''' This function will login into the EMA platform using the user name and password supplied.'''
    debug.p(" FUNC: ema_function.emaLogin(Username, Password)       : ")
    insert_xml = __readinxml__('./login.xml')
    sequence_id = ''
    session_id = ''
    return_code = None
    insert_xml = insert_xml.format(ema_username, ema_password)
    debug.p(insert_xml)
    headers ={'content-type':'text/xml; charset=utf-8','content-length':'503',  'SOAPAction':'CAI3G#Login'}
    r= requests.post('http://'+ema_host +':'+ ema_port, data = insert_xml, headers = headers, auth =(ema_username, ema_password))
    if r.status_code != 200:
        print (' ERROR: An error has occurred trying to login into the EMA platform.')
        print (r.status_code)
        print (r.text)
    else:
        tree= ET.fromstring(r.text)
        for node in tree.getiterator():
            print node.tag, node.attrib, node.text
            if node.tag == '{http://schemas.ericsson.com/cai3g1.2/}baseSequenceId': sequence_id = node.text
            if node.tag == '{http://schemas.ericsson.com/cai3g1.2/}sessionId' : session_id = node.text
        if sequence_id !='' and session_id !='':
            debug.p  (('Sequence Id 1 :   {0}    ::::: Session Id 1 :   {1}').format (sequence_id, session_id))
            session = { "sequence_id" : sequence_id, "session_id": session_id, "transaction_id" : "12334455", "ema_host": ema_host, "ema_port": ema_port}
            return_code = (session)
    return (return_code) # Return login information for future requests

def ema_logout(session_id):
    ''' This function will logout of the EMA platform using the session id supplied.'''
    debug.p(" FUNC: ema_logut   : ")
    XML = open('./logout.xml','r')
    insert_xml = XML.read().format(session_id)
    debug.p(insert_xml)
    headers ={'content-type':'text/xml; charset=utf-8',  'SOAPAction':'CAI3G#Logout'}
    r= requests.post('http://'+ema_host +':'+ ema_port, data = insert_xml, headers = headers, auth =('sogadm', 'sogadm'))
    if r.status_code != 200:
        print (' ERROR: An error has occurred trying to logout of the EMA platform.')
        print (r.status_code)
        print (r.text)
    else:
        print (' Logout successfull!!!!')
        print (r.text)
    return


def emaGetImsSubscriber(sub, session):
    ''' This function will search EMA for a specified IMS subscription and retrieve subscription information.
        This function takes a subscriberId as input and returns the subscription xml.
        The sequenceId, transaction_id and sessionId must alos be supplied.
        This function returns an XML string of Subscriber Information or Error Information.
    '''
    debug.p('Func::: emaGetImsSuscriber      : ')

    insert_xml = __readinxml__('./get_ims_sub.xml').format(session['sequence_id'], session['transaction_id'],session['session_id'], sub.subscriberId)
    debug.p(insert_xml)
    
    headers ={'content-type':'text/xml; charset=utf-8',  'SOAPAction':'CAI3G#Get'}
    r= requests.post('http://'+session['ema_host'] +':'+ session['ema_port'], data = insert_xml, headers = headers)
    if r.status_code != 200:
        print (' ERROR: An error has occurred trying to retrieve the subscription::: {0}    from the EMA platform.').format(sub.subscriberId)
        print (r.status_code)
        print (r.text)
    else:
        print (' Subscription found!!!!')
        print (r.text)
    return (r)

def emaCreateImsSubscriber(sub, session):
    ''' This function will create an IMS subscriber/subscription on HSS and ENUM via EMA.
        The inputs for this subscription are the session/sequence/transaction ids 
        and the subscriber information itself.
    '''
    debug.p('FUNC:: emaCreateImsSubscriber      :   ')

    insert_xml = __readinxml__('./create_ims_subscriber.xml').format(session['sequence_id'], session['transaction_id'],session['session_id'], sub.subscriberId, sub.chargingProfId, sub.pubData.publicIdValue, sub.pubData.publicIdTelValue, sub.pubData.phoneContext, sub.pubData.privateUserId, sub.origProfileId, sub.termProfileId)
    headers ={'content-type':'text/xml; charset=utf-8', 'SOAPAction':'CAI3G#Create'} 

    debug.p(insert_xml)

    r= requests.post('http://'+session['ema_host'] +':'+ session['ema_port'], data = insert_xml, headers = headers)
    if r.status_code != 200:
        print (' ERROR: An error has occurred trying to create the subscription::: {0}    on the EMA platform.').format(sub.subscriberId)
        print (r.status_code)
        print (r.text)
    else:
        print (' Subscription Created !!!!')
        print (r.text)
    return (r)

def emaDeleteImsSubscriber(subscriber,session):
    ''' This function will create an IMS subscriber/subscription on HSS and ENUM via EMA.
        The inputs for this subscription are the session/sequence/transaction ids 
        and the subscriber (class instance)information itself.
    '''
    debug.p('FUNC:: emaDeleteImsSubscriber      :   ')

    insert_xml = __readinxml__('./delete_ims_subscriber.xml').format(session['sequence_id'], session['transaction_id'],session['session_id'], subscriber.subscriberId)
    headers ={'content-type':'text/xml; charset=utf-8', 'SOAPAction':'CAI3G#Delete'} 

    debug.p(insert_xml)

    r= requests.post('http://'+session['ema_host'] +':'+ session['ema_port'], data = insert_xml, headers = headers)
    if r.status_code != 200:
        print (' ERROR: An error has occurred trying to delete the subscription::: {0}    on the EMA platform.').format(subscriber.subscriberId)
        print (r.status_code)
        print (r.text)
    else:
        print (' Subscription Deleted !!!!')
        print (r.text)
    return (r)

if __name__ == "__main__":
    main()


