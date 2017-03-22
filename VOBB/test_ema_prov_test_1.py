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

import ema_functions as ema
from time import sleep
import csv
from datetime import datetime
import debug


"""
    EMA LOGIN INFORMATION
"""
username= 'sogadm'
ema_password = 'sogadm'
#ema_host = '10.147.21.198'  # Live Node
ema_host = '10.16.6.228'   # Test Plant
ema_port = '8998'

'''
subscriberId = '+353762376176@voice.eir.ie'
msisdn = '+353762376176'
domain = 'voice.eir.ie'
password = 'qwerty'
publicId = 'sip:{0}'.format(subscriberId)
'''

init_sub = 353771000000
final_sub = 353771000020
listofsubs = []
results_of_create_subs = []
results_of_delete_subs = []
results_of_get_subs = []
results_of_get_dns = []

def write_to_file(results):
    """
    """
    f = open('./report.csv', 'a')
    try:
        writer = csv.writer(f)
        writer.writerow((setTime(), results))
    finally:
        f.close()
    return


    
def setTime ():
    """ This function returns the real time in a format required for the program.
    
    Good example of datetime:::::::::: real_Time = datetime.datetime.now ().strftime(date_format)

    """

    debug.p("Func: setTime in appCheck.py")
    time_format = "%Y-%m-%d %H:%M:%S"
    app_time_format = "%Y-%m-%d %H:%M"
    real_Time = datetime.now ()
    real_Time = real_Time.strftime (time_format)
    return real_Time



class vobb_sub(object):
    """
        
    """
    domain  = 'voice.eir.ie'
    plus = '+'
    at = '@'

    def __init__(self, number):

        number = str(number)
        self.subscriberId = self.plus + number + self.at +  self.domain 
        self.msisdn = self.plus + number
        self.password = 'qwerty'
        self.publicId = 'sip:{0}'.format(self.subscriberId)


def set_up_subs_list():
    """
    """
    for sub in range(init_sub, final_sub, 1):
        x = vobb_sub(sub)
        listofsubs.append(x)
    return

def create_sub_range(session):
    """
        This function will create the subscriptions in the range.
    """
    print (setTime())
    print('Starting Provisioning Exercise')
    for x in listofsubs:
        try:
            print (("{0} --- Provision subscriber : {1}").format(setTime(), x.subscriberId))        
            result = ema.emaCreateVobbSubscriber(session, x.msisdn, x.subscriberId, x.publicId, x.domain, x.password)
            sleep(0.5)
        except Exception, (e):
            print ("Exception!!!!")
            print (e)
        finally:
           results_of_create_subs.append(result.status_code)
           pass
    write_to_file(results_of_create_subs)
    return

def get_sub_range(session):
    """
    """
    print ('Starting The retrieval of the subs from EMA!')
    for sub in listofsubs:
        print (('{0} Start retrieval of {1}').format(setTime(), sub.subscriberId))
        l = []
        l.append(sub.msisdn)
        try:
            for attempt in range(0,5,1):
                result = ema.emaGetVobbSubscriber(session, sub.subscriberId)
                l.append(result.status_code)
                sleep(0.5)

        except Exception, e:
            print ("Exception!!!!")
            print (e)
        finally:    
            results_of_get_subs.append(l)
    write_to_file(results_of_get_subs)
    return

def get_dns_range(session):
    """
    """
    print ('Starting The retrieval of the DNS from EMA!')
    for sub in listofsubs:
        print (('{0} Start DNS retrieval of {1}').format(setTime(), sub.subscriberId))
        l = []
        l.append(sub.msisdn)
        try:
            for attempt in range(0,20,1):
                result = ema.emaGetDnsEntry(session, sub.msisdn, sub.subscriberId)
                l.append(result.status_code)
                sleep(0.5)

        except Exception, e:
            print ("Exception!!!!")
            print (e)
        finally:
            results_of_get_dns.append(l)
    write_to_file(results_of_get_dns)
    return


def delete_sub_range(session):
    """
        This function will delete the subscriptions in the range.
    """
    print ("Starting Deletion of Subs")

    to_be_removed = []

    for sub in listofsubs:
        try:
            result = ema.emaDeleteVobbSubscriber(session, sub.msisdn, sub.domain)
            print (('{0} -- Delete {1}').format(setTime(), sub.subscriberId))
            to_be_removed.append(sub)
            sleep(0.5)
            results_of_delete_subs.append(result.status_code)
            pass
        except Exception, (e):
            print ("Exception!!!!")
            print (e)
        finally:
            pass
    for entry in to_be_removed:
        listofsubs.remove(entry)
    write_to_file(results_of_delete_subs)
    return

def main():
    """
        This is the main program body. 
    """
    try:
        print ('Starting Session')
        session = {}
        session['emaSession'] = ema.emaLogin()
        session['sub_pw'] = 'yyeeetteoe'

        set_up_subs_list()
        create_sub_range(session)
        get_sub_range(session)
        get_dns_range(session)
        delete_sub_range(session)

    finally:
        ema.ema_logout(session['emaSession'])       
        print ('Session Closed')

        print ('################# GET RESULTS ##############')
        print ( results_of_get_subs)
        print ('################# CREATE RESULTS ##############')
        print ( results_of_create_subs)
        print ('################# DELETE RESULTS ##############')
        print (results_of_delete_subs)
        print ('################# GET DNSS ##############')
        print ( results_of_get_dns)


if __name__ == "__main__":
    main()


