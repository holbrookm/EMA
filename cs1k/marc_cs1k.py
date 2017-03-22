#!/usr/bin/python

""" This script will access the EMA via http commands with SOAP XML content.
    This will test Ivica's xml for vobb.
    # 0851742253
    # <mholbrook@eircom.ie>
"""
from __future__ import print_function
import sys
sys.path.insert(0, '/home/ema-gui/emalive')
import ema_functions as ema
import requests
from requests.auth import HTTPBasicAuth
import class_ims_ema as ims
from time import sleep
import json
import csv

ema_username= 'sogadm'
ema_password = 'sogadm'
#ema_host = '10.147.21.198'  # Live Node
ema_host = '10.16.6.228'   # Test Plant
ema_port = '8998'

filename = 'subs.csv'

#Next 3 lines to setup prov logging
import cs1k_logging_config as cs1klog
cs1klog.setup_logger('prov', './provisioning.log')
prov_logger = cs1klog.logging.getLogger('prov')

logger = cs1klog.logger 

eirin11_put_request = 'http://10.146.3.12:8182/cie-rest/provision/accounts/global/lists/eircomGnpTable/entries/null'
eirin04_put_request = 'http://10.147.48.100:8182/cie-rest/provision/accounts/global/lists/eircomGnpTable/entries/null'
eirin11_query_request = 'http://10.146.3.12:8182/cie-rest/provision/accounts/global/lists/eircomGnpTable/entries/'
eirin04_query_request = 'http://10.147.48.100:8182/cie-rest/provision/accounts/global/lists/eircomGnpTable/entries/'

def NGINPort(sub):
    ''' This function will create an IMS subscriber/subscription on HSS and ENUM via EMA.
        The inputs for this subscription are the session 
        and the subscriber information itself.
    '''
    #json_data = open ('./templates/subs.json') 
	#data = json.load (json_data)
	#json_data.close()
    
    json_data = open('/home/ema-gui/emalive/cs1k/gnp_port_in.json','r') #.read().replace('\n', '')
    #json_data = json_data.replace('\r', '')
    
    jdata = json.load(json_data)
    headers ={'content-type':'application/json; charset=utf-8'} 

    
    #for row in jdata: print (row)
    if sub[0] == '+':
        jdata['fields']['number'] = sub[1:] # This adds the sub number into the json for repacking and submission.
        jdata['id'] = sub[1:]
    else:
        jdata['fields']['number'] = sub
        jdata['id'] = sub

    json_data =json.dumps(jdata)
    r= requests.put(eirin11_put_request, auth =('admin1', '$Password1'),  data = json_data, headers = headers)
    #r= requests.put(eirin11_put_request, auth =('admin', 'password'),  data = json_data, headers = headers)

    if r.status_code != 200 or r.status_code !=401 or r.status_code != 201:
        #logger.error (' ERROR: An error has occurred trying to port the subscription::: {0}    on the NGIN Platform.').format(sub)
        logger.error (r.status_code)
        logger.error (r.text)
    elif r.status_code == 401:
        logger.error (r.status_code)
        logger.error (r.text)
        print ('Unauthorised Access : Check Username/password')
    else:
        prov_logger.info ((' NGIN PORT: {0}Subscription Created !!!!').format(jdata['id']))
        prov_logger.debug (r.text)
    logger.debug('**Leaving FUNC :::: NGINPOrt')
    return (r)
    
def verifyPort(sub):
    ''' This function verify if the input number sub exists on the NGIN Portability database.
        Input (sub)   
        Output (request output)        
    '''
    logger.debug('*Entering FUNC :::: NGINPort')
    
    headers ={'content-type':'application/json; charset=utf-8'} 
    #userdetails = ('admin', 'password')
    userdetails = ('admin1', '$Password1')
    query_string = str(eirin11_query_request + str(sub))
    
    r= requests.get( query_string, auth = userdetails, headers = headers)
    
    if r.status_code == 204:
        prov_logger.info (('Subscription {0} is not Ported!!!').format(sub))
        logger.debug (r.text)
        print (('Subscription {0} is not Ported!!!').format(sub))
    elif r.status_code == 200:
        prov_logger.info (('Subscription {0} is Already Ported !!!!').format(sub))
        logger.debug (r.text)
        print (('Subscription {0} is Already Ported !!!!').format(sub))
 
    elif r.status_code !=401:
        print ('Unauthorised Access : Check Username/password')
    else :
        logger.error (('ERROR: An error has occurred trying to verify the subscription port status::: {0}    on the NGIN Platform.').format(sub))
        logger.error(query_string)
        logger.error (r.status_code)
        #logger.error (r.text)
        print (('ERROR: An error has occurred trying to verify the subscription port status::: {0}    on the NGIN Platform.').format(sub))
       
        logger.debug('**Leaving FUNC :::: NGINPOrt')
    return (r)
 
def checkforfile(filename):
    """ The is the function to check for an existing output file.
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
        pw = row[1]
        entry = (sub_no, pw)
        sublist.append(entry)
    return sublist



def check_list_for_existing_ports (subdata):
    """
        This function takes sub/pw tuple, checks to see if already ported.
        If already ported, remove from provisioning list and place in own list. 
        Return both lists.
    """
    list_of_existing_ports =[]
    not_ported_subs = []
    count = 0 # count needed for subdata list pop if required.
    for row in  subdata:
        print (" Checking {0} in NGIN GNP Database.".format(row[0]))
        prov_logger.info(" Checking {0} in NGIN GNP Database.".format(row[0]))
        r = verifyPort(row[0]) # Function call to NGIN
        if r.status_code == 401:
            print ('Unauthorised Access : Check Username/password')          
        elif r.status_code == 200:
            list_of_existing_ports.append(row[0])
            print ("{0} is already ported.".format(row[0]))
            prov_logger.info ("{0} is already ported.".format(row[0]))
        elif r.status_code == 204:
            print ("{0} is not in the GNP Database and will continue.".format(row[0]))
            prov_logger.info ("{0} is not in the GNP Database and will continue.".format(row[0]))
            not_ported_subs.append(row)
        count += 1 #List increment        
    return list_of_existing_ports, not_ported_subs

def check_ngin_access(subdata):
    """
        Use this function to verify correct username and PW.
    """
    r = verifyPort(999)
    print (r.status_code)
    if r.status_code == 204:
        return True
    else:
        return False
    """
    if (subdata[0][0]):
        return True  
    else:
        return False
    """


def check_existing_ho_subs(sub_no):
    """
    """    
    s1 = ims.hostedOfficeSubscriber(sub_no)
    session = {}
    session['emaSession'] = ema.emaLogin()
    result = s1.subscriberGet(session)
    ema.ema_logout(session['emaSession'])
    sleep(0.25)
    #print (result.text)
    return result
    
def create_hosted_office(sub, pw):
    """ 
        Create the hosted office subscription.
    """    
    s1 = ims.hostedOfficeSubscriber(sub)
    session = {}
    session['emaSession'] = ema.emaLogin()
    session['sub_pw'] = pw    # Get password from xls sheet and put here

    result = s1.subscriberCreate(session)
    ema.ema_logout(session['emaSession'])
    return result    


def main():    
    """
    """
    existing_ho = []
    completed_provisions = []

    subdata =importDetails(checkforfile(filename))
    logger.debug(subdata) # Just for logging purposes
    if check_ngin_access(subdata):
        print ('ACCESS GRANTED TO NGIN')
        ports, checked_subdata = check_list_for_existing_ports (subdata) 
        # checked_subdata is the list of numbers to be ported!
        # ports is the list of number already ported. 
        for row in checked_subdata:
            sub = str('+' + str(row[0]))
            print ("Checking for Hosted Office subscription {0}".format(sub)) 
            r = check_existing_ho_subs(sub)
            sleep(0.25)
            if r.status_code == 200:
                existing_ho.append(row[0])
                prov_logger.error(("The subscription {0} is already provisioned on the BW Platform. Please verify!!").format(sub))
                print (("The subscription {0} is already provisioned on the BW Platform. Please verify!!").format(sub))
                while(True):
                            print ("Do you want to port anyway? y/n")
                            answer = raw_input()
                            if answer == 'y':
                                result_of_port = NGINPort(row[0])
                                if result_of_port.status_code == 200 or result_of_port.status_code == 201:
                                    prov_logger.info(("GNP ONLY subscription {0} created !").format(sub))
                                    print (result_of_port.status_code)        
                                    completed_provisions.append(row[0])
                                    break
                                else:
                                    print (result_of_port.status_code)
                                    logger.error( result_of_port.status_code )
                                    logger.error( result_of_port.text )
                                    print ((" FAIL :Subscription {0} port failed !").format(sub))
                                    break
                            elif answer == 'n':
                                break
                            else:
                                print ("Please answer y or n only")
                                pass
                                
            elif r.status_code == 500: # If subscription does not exist then go create
                action = create_hosted_office(sub, row[1])
                sleep(.25)
                #action = check_existing_ho_subs(sub) # Debug code only Please comment out for live action
                #action.status_code = 500 # Debug code please comment out for real operation 
                if action.status_code == 200:
                    print (("Broadworks Subscription {0} created !").format(sub))
                    prov_logger.info(("Broadworks Hosted Office Subscription {0} created !").format(sub))
                    result_of_port = NGINPort(row[0])
                    if result_of_port.status_code == 200 or result_of_port.status_code == 201:
                        print (result_of_port.status_code)
                        logger.info( result_of_port.text )
                        print ((" Subscription {0} ported !").format(sub))
                        prov_logger.info((" Subscription {0} ported !").format(sub))
                        completed_provisions.append(row[0])        
                    else:
                        prov_logger.error( result_of_port.text )
                        prov_logger.error(("GNP FAIL:Broadworks subscription {0} created !").format(sub))
                        print (result_of_port.status_code)
                        
                else:
                    logger.error(action.text)
                    prov_logger.error(("CHECK ISSUE WITH HOSTED OFFICE PROVISION for {0}").format(sub))
                    print(("CHECK ISSUE WITH HOSTED OFFICE PROVISION for {0}").format(sub))

        print ('The following numbers exist within the porting database already and will not be processed further. Please investigate!')
        print("There are {0} ported subscriptions already !".format(ports.__len__()))
        print (ports)
        print ("The following numbers already existed within Hosted Office, please check!")
        print("There are {0} existing HO subscriptions!".format(existing_ho.__len__()))
        print (existing_ho)
        print("The following are the completed subscriptions!")
        print("There are {0} completed subscriptions!".format(completed_provisions.__len__()))
        print (completed_provisions)
        print ("Provisioning Data!!")
        print ("There are {0} subscriptions in total!".format(checked_subdata.__len__()))
        print(checked_subdata)    
    
    

if __name__ == "__main__":
#    print ('Start')
    main() 


"""
print ("Testing CS1K Provisioning")
sub_no = '+353771234567'

s1 = ims.hostedOfficeSubscriber(sub_no)
session = {}
session['emaSession'] = ema.emaLogin()
session['sub_pw'] = 'yyeeetteoe'    # Get password from xls sheet and put here

result = s1.subscriberCreate(session)
print (result)
print (result.text)


result = NGINPort(sub_no)
print (result)
print (result.text)


result = s1.subscriberDelete(session)
print (result)
print (result.text)
"""
