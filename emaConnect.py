#!/usr/bin/python

""" This script will access the EMA via http commands with SOAP XML content.
    #Marc Holbrook
    # 0851742253
    # <mholbrook@eircom.ie>
"""
import debug, logging_config
import requests
from xml.etree import ElementTree as ET

ema_username= 'sogadm'
ema_password = 'sogadm'
ema_host = '10.16.6.228'
ema_port = '8998'

logger = logging_config.logger

def __readinxml__(f):
    ''' Internal method to read in XML file for use within package functions.
    '''
    logger.debug('Method : ema_functions.__readinxml__')

    XML = open(f,'r')
    _xml = XML.read()
    return (_xml)

def emaLogin():
    ''' This function will login into the EMA platform using the user name and password supplied.'''
    logger.debug(" FUNC: emaConnect.ema_login(Username, Password)       : ")
    insert_xml = __readinxml__('./login.xml')
    sequence_id = ''
    session_id = ''
    return_code = None
    insert_xml = insert_xml.format(ema_username, ema_password)
    logger.debug(insert_xml)
    headers ={'content-type':'text/xml; charset=utf-8','content-length':'503',  'SOAPAction':'CAI3G#Login'}
    r= requests.post('http://'+ema_host +':'+ ema_port, data = insert_xml, headers = headers, auth =(ema_username, ema_password))
    if r.status_code != 200:
        logger.error (' ERROR: An error has occurred trying to login into the EMA platform. User : ' + ema_username)
        logger.error (r.status_code)
        logger.error (r.text)
    else:
        logger.log( INFO, "HTTP-200 successful Login request for " + ema_username)
        tree= ET.fromstring(r.text)
        for node in tree.getiterator():
            print node.tag, node.attrib, node.text
            if node.tag == '{http://schemas.ericsson.com/cai3g1.2/}baseSequenceId': sequence_id = node.text
            if node.tag == '{http://schemas.ericsson.com/cai3g1.2/}sessionId' : session_id = node.text
        if sequence_id !='' and session_id !='':
            logger.debug  (('Sequence Id 1 :   {0}    ::::: Session Id 1 :   {1}').format (sequence_id, session_id))
            session = { "sequence_id" : sequence_id, "session_id": session_id, "transaction_id" : "12334455", "ema_host": ema_host, "ema_port": ema_port}
            return_code = (session)
    return (return_code) # Return login information for future requests
    
def emaLogout(session):
    ''' This function will logout of the EMA platform using the session id supplied.'''
    logger.debug(" FUNC: ema_logut   : ")
    XML = open('./ema_logout.xml','r')
    insert_xml = XML.read().format(session['session_id'])
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
    return    
