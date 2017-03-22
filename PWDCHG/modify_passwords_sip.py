#!/usr/bin/python

""" This script will access the EMA via http commands with SOAP XML content.
    This will modify the private user Passowrds in the HSS via EMA.
    # 0851742253
    # <mholbrook@eircom.ie>
"""

from __future__ import print_function
import sys
sys.path.insert(0, '/home/ema-gui/emalive')
import ema_functions as ema
import class_ims_ema as ims
from time import sleep
import json
import csv
import pwd_logging_config
import m_password


logger = pwd_logging_config.logger

filename = 'subs1-50.csv'
output_path = './output1-50.csv'


def checkforfile(filename):
    """ The is the function to check for an existing input file.
    """
    try:
        inputlist =[]
        with open(filename,'ra') as fin:
            reader = csv.reader(fin)
            for row in reader:
                if row[0]!= '':
                    inputlist.append(row)
            print (" File Exists. It has ", len(inputlist), " number of entries" )      
                
    except IOError as (errno, strerror):
        print ("IOError : ({0}) : {1}".format(errno, strerror))

    finally:
        fin.close()
        return inputlist
        

def importDetails(details):
    """
        This function will import the subscription details from a designated csv file.
        The output is a list of sub/pw tuples.
    """
    sublist = []
    sub_no =''
    for row in details:
        sub_no =  row[0].rsplit('@')[0]
        
        entry = (sub_no)
        sublist.append(entry)
    return sublist
    
def modify_password_rw(sub_no, pw = None):
    """
        Check if Sip T rw sub exists
    """    
    m_result = False
    s1 = ims.remoteWorker(sub_no)
    session = {}
    session['emaSession'] = ema.emaLogin()
    result = s1.subscriberGet(session)
    if result.status_code == 200:
        m_result = s1.subscriberModifyPassword(session, pw)
    ema.ema_logout(session['emaSession'])
    sleep(0.25)
    #print (m_result.text)
    return m_result

def csv_writer(data, path):
    """
    Write data to a CSV file path
    """
    with open(path, "wb") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for line in data:
            writer.writerow(line)
    return
    
    

p = m_password.id_generator(16)

#modify_password_rw ('+353214276631', p )
#modify_password_rw ('+353567721222', p )
#modify_password_rw ('+353768920808', 'manu16!"QW' )


#l = [353567721432, 353567721200, 353766902161, 353766969793, 353766969794, 353766969878, 353766969879 ,353766969880, 353768920806]
inputlist = checkforfile(filename)
mod_input_list = importDetails(inputlist)

prov_list = []
for num in mod_input_list:
    p = m_password.id_generator(16)
    if num[0] != '+':
        modnum = ('+' + str(num))
    else:
        modnum = str(num)

    if not (modify_password_rw(modnum, p)):
        p = 'SUB is not provisioned'
    sub_tuple = (modnum, p)
    prov_list.append(sub_tuple)

for elem in prov_list:
    print (elem[0] + ' : ' + elem[1])
    
csv_writer(prov_list, output_path)
print('The End.')


    
