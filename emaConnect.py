#!/usr/bin/python

""" This script will access the EMA via http commands with SOAP XML content.
    #Marc Holbrook
    # 0851742253
    # <mholbrook@eircom.ie>
"""
import debug
import requests
from xml.etree import ElementTree as ET

ema_username= 'sogadm'
ema_password = 'sogadm'
ema_host = '10.16.6.228'
ema_port = '8998'

def __readinxml__(f):
    ''' Internal method to read in XML file for use within package functions.
    '''
    debug.p('Method : ema_functions.__readinxml__')

    XML = open(f,'r')
    _xml = XML.read()
    return (_xml)

def emaLogin():
    ''' This function will login into the EMA platform using the user name and password supplied.'''
    debug.p(" FUNC: emaConnect.ema_login(Username, Password)       : ")
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
    
def emaLogout(session):
    ''' This function will logout of the EMA platform using the session id supplied.'''
    debug.p(" FUNC: ema_logut   : ")
    XML = open('./logout.xml','r')
    insert_xml = XML.read().format(session['session_id'])
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
