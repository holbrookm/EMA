#!/usr/bin/python

""" This script will access the RNF ssDNS via ssh.
    This will test Ivica's xml for vobb.
    # 0851742253
    # <mholbrook@eircom.ie>

 WEB PAGE INFO : 10.144.134.36:8080/ipworks/webapp/login
"""

from __future__ import print_function
import sys

sys.path.insert(0, '/home/ema-gui/emalive')

import requests
from requests.auth import HTTPBasicAuth
import ema_functions as ema
import class_ims_ema as ims





username= 'sogadm'
ema_password = 'sogadm'
#ema_host = '10.147.21.198'  # Live Node
ema_host = '10.16.6.228'   # Test Plant
ema_port = '8998'


subscriberId = '+353768888888@voice.eir.ie'
msisdn = '+353768888888'
domain = 'voice.eir.ie'
password = 'qwerty'
publicId = 'sip:{0}'.format(subscriberId)


session = {}
session['emaSession'] = ema.emaLogin()
session['sub_pw'] = 'yyeeetteoe'

print (session)
results_stats = []
try:
    result = ema.emaCreateVobbSubscriber(session, msisdn, subscriberId, publicId, domain, password)
    results_stats.append(result.status_code)
    print (result.text)
finally:
    ema.ema_logout(session['emaSession'])

print (results_stats)
