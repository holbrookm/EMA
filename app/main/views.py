#!/usr/bin/python
""" This is the Flask Web dev that front ends the EMA functions.
    Broadworks functions were added March 17.
    #
    # 0851742253
    # <mholbrook@eircom.ie>
    Modified 13/3/17: Marc Holbrook: Added Broadworks type checks for Fraud Mgmt.
                                    May be housed elsewhere later.
    
"""

import sys, os
from flask import Flask, request, render_template, url_for, redirect, flash, session, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.login import login_user, logout_user, login_required
from .forms import LoginForm, BWForm # I think the dot represents this folder/project...

from config import config

import debug, logging_config
import class_ims_ema as ims
import ema_functions as ema
#import session_calls



# BW related imports here 
import string
import ocip_functions as ocip
import mysockets
reload(sys)
sys.setdefaultencoding("utf-8")
import csv
from time import sleep
import scriptio as sio
import xmltodict

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

# End of BW related imports



#Blueprint required imports
from . import main
from .. import db
from ..models import User



logger = logging_config.logger
################################

@main.route('/',  methods=['POST','GET',])
@main.route('/login',  methods=['POST','GET',])
@main.route('/index',  methods=['POST','GET',])
def index():
    """ Index Page.
    """
    # check for existing session in browser cookies
    try:
        ema.ema_logout(session['emaSession']['session_id'])
        session.clear()
        logout_user()
    except:
        pass
    logger.debug('FUNC::::::: app.main.route.index')
    form = LoginForm()
    
    if form.validate_on_submit():
        logger.debug ('Performing logon')
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        
        user = User.query.filter_by(username = request.form['username']).first()
        if user is not None and user.verify_password(request.form['password']):
            login_user(user)
            session['emaSession'] = ema.emaLogin()
            return redirect(url_for(('main.subscribers')))
        flash('Invalid Username and Password')
    
    logger.debug('** Leaving FUNC::::::: app.main.route.index')
    return render_template('/login.html', form = form)   # I believe that this is the first function/view called


@main.route('/logout')
@login_required
def logout():
    logger.debug('FUNC:::::: app.route.logout')
    ema.ema_logout(session['emaSession']['session_id'])
    session.clear()
    logout_user()
    logger.debug('** Leaving FUNC:::::: app.route.logout')
    flash ('Logged Out')
    return redirect(url_for(('main.index')))


    
#############################
#### SEARCH #########
#############################

@main.route('/searchRangeR')
@login_required
def searchRangeR():
    logger.debug('FUNC:::::: app.route.searchRangeR')
    logger.debug('** Leaving FUNC:::::: app.route.searchRangeR')
    return render_template('searchRangeR.html')

@main.route('/performSearchRangeR', methods=['POST', ])
@login_required
def performSearchRangeR():
    session.permanent = True
    logger.debug(('FUNC:::::: app.route.performSearchRangeR           {0}').format(request.method))  
    if request.method == 'POST':
        sub = str(request.form['sub'])
        if sub == "": 
            return redirect(url_for('main.subscribers'))
        session['sub'] = sub   # subscriber number in text
        c_sub = ims.registeredRangeSubscriber(sub)
        debug.p(session)
        result = c_sub.subscriberGet(session)
        logger.debug (result.status_code)
        logger.debug (result.text)

        if result.status_code == 500: #Successful EMA connection but there is an error.
            if result.text.find('Invalid Session') != -1:
                logger.debug(('** Leaving FUNC:::: app.route.performSearchrangeR:  Invalid Session'))
                return redirect(url_for('auth.login', error='Invalid Session'))
            elif result.text.find('No such object') != -1:
                logger.debug(('** Leaving FUNC:::: app.route.performSearchrangeR:  Subscriber not provisioned: redirecting to subscribers.html'))
                session['mesg'] = 'NotProvisioned'
                return redirect(url_for('main.subscribers'))
            else:
                pass
        if result.status_code == 200:
            subdetails = ema.prepareXmlToClass(result.text)
            if isinstance(subdetails['pubData'],list):
                session['count'] = subdetails['pubData'].__len__()
                session['subType'] = subdetails['pubData'][0]['publicIdState'] # Current Subscriber State in text
                session['details'] = subdetails  # Current Subscriber SOAP XML structure
            else:
                session['count'] = 0
                session['subType'] = subdetails['pubData']['publicIdState'] # Current Subscriber State in text
                session['details'] = subdetails  # Current Subscriber SOAP XML structure

            del c_sub # Remove Subscriber Class instance

            logger.debug('**Leaving FUNC:::::: app.route.performSearchRangeR: Status = 200')
            return redirect(url_for('main.subscriberResult'))
            
    else:
        return redirect(url_for('auth.login', error='Unknown error Condition'))
        logger.error('Unexpected error occurred in app.route.performSearchRangeR ')
    logger.debug('** Leaving FUNC::::::: app.route.performSearchRangeR: End of Func error')
    return redirect(url_for('auth.login', error='Unknown error Condition'))


#############################
#### CREATE
#############################

@main.route('/subscriberCreate')
@login_required
def subscriberCreate():
    logger.debug('FUNC:::::: app.route.subscriberCreate')
    logger.debug('** Leaving FUNC::::::: app.route.subscriberCreate')
    return render_template('searchRangeR.html', createmesg= 'True')

@main.route('/CreateNR/<sub>', methods=['POST','GET',])
@login_required
def createNR(sub):
    logger.debug(('FUNC:::::: app.route.createNR           {0}').format(request.method))
    c_sub = ims.nonRegisteredSubscriber(sub)
    result = c_sub.subscriberCreate(session)
    
    if result.status_code == 500: #Successful EMA connection but there is an error.
        if result.text.find('Invalid Session') != -1:# -1 means does not exist, therefore if True it exists.
            logger.debug(('** Leaving FUNC:::: app.route.createNR:  Invalid Session'))
            return redirect(url_for('auth.login', error='Invalid Session'))
        elif result.text.find('already exists') != -1: # -1 means does not exist, therefore if True it exists.
            logger.debug(('** Leaving FUNC:::: app.route.createNR:  Subscriber Already Exists'))
            session['mesg'] = 'ExistingSubscriber'
            return redirect(url_for('main.subscribers'))
        else:
            logger.debug('Unknown Error in createNR func')
            pass
    elif result.status_code == 200:
        session['mesg'] = 'Created'
        session['sub'] = sub
        del c_sub # Remove Subscriber Class instance
        logger.debug('** Leaving FUNC::::::: app.route.createNR')
        return redirect(url_for('main.subscribers'))
    else:
        logger.debug(('** Leaving FUNC::::::: app.route.createNR :::  Unknown Condition ::  {0}').format(result.status_code))
        return redirect(url_for('auth.login', error='Unknown error Condition'))
 


@main.route('/CreateR/<sub>', methods=['POST','GET',])
@login_required
def createR(sub):
    logger.debug(('FUNC:::::: app.route.createR           {0}').format(request.method))
    c_sub = ims.registeredSubscriber(sub)# Create Registered Subscriber Class instance
    result = c_sub.subscriberCreate(session)
   
    if result.status_code == 500: #Successful EMA connection but there is an error.
        if result.text.find('Invalid Session') != -1:
            logger.debug(('** Leaving FUNC:::: app.route.createR:  Invalid Session'))
            return redirect(url_for('auth.login', error='Invalid Session'))
        elif result.text.find('already exists') != -1: # -1 means does not exist, therefore if True it exists.
            logger.debug(('** Leaving FUNC:::: app.route.createR:  Subscriber Already Exists'))
            session['mesg'] = 'ExistingSubscriber'
            return redirect(url_for('main.subscribers'))
        else:
            logger.debug('Unknown Error in createR func')
            pass
    if result.status_code == 200:
        session['mesg'] = 'Created'
        session['sub'] = sub
        del c_sub # Remove Subscriber Class instance
    
    logger.debug('** Leaving FUNC::::::: app.route.createR')
    return redirect(url_for('main.subscribers'))
 
 
@main.route('/CreateHostedOffice/<sub>' , methods=['POST','GET',])
@login_required
def createHostedOffice(sub):
    logger.debug(('FUNC:::::: app.route.createHostedOffice           {0}').format(request.method))
    session['sub_pw'] = str(request.form['pw'])
    c_sub = ims.hostedOfficeSubscriber(sub)
    result = c_sub.subscriberCreate(session)
    if result.status_code == 500: #Successful EMA connection but there is an error.
        if result.text.find('Invalid Session') != -1:
            logger.debug(('** Leaving FUNC:::: app.route.createHostedOffice:  Invalid Session'))
            return redirect(url_for('auth.login', error='Invalid Session'))
        elif result.text.find('already exists') != -1: # -1 means does not exist, therefore if True it exists.
            logger.debug(('** Leaving FUNC:::: app.route.createHostedOffice:  Subscriber Already Exists'))
            session['mesg'] = 'ExistingSubscriber'
            flash (session['mesg'])
            return redirect(url_for('main.subscribers'))
        elif  result.text.find('userPassword is illegal') != -1: # -1 means does not exist, therefore if True it exists.
            logger.debug(('** Leaving FUNC:::: app.route.createHostedOffice: Incorrect Password format or Blank. '))
            session['mesg'] = 'The Password submitted was illegal or blank.'
            flash (session['mesg'])
            return redirect(url_for('main.subscribers'))
        else:
            logger.debug('Unknown Error in createHostedOffice func')
            session['mesg'] = ('Unknown error creating Subscriber: {0}'.format(result.text))
            flash('Unknown error creating Subscriber. Check Log files')
            return redirect(url_for('main.subscribers'))
    
    elif result.status_code == 200:
        session['mesg'] = 'Created'
        session['sub'] = sub
        del c_sub # Remove Subscriber Class instance
        logger.debug('** Leaving FUNC::::::: app.route.createHostedOffice')
        return redirect(url_for('main.subscribers'))
    else:
        logger.debug(('** Leaving FUNC::::::: app.route.createHostedOffice :::  Unknown Condition ::  {0}').format(result.status_code))
        logger.debug(('** Leaving FUNC::::::: app.route.createHostedOffice :::  Unknown Condition ::  {0}').format(result.text))
        return redirect(url_for('auth.login', error='Unknown error Condition'))
 

@main.route('/CreatePilot/<sub>' , methods=['POST','GET',])
@login_required
def createPilot(sub):
    logger.debug(('FUNC:::::: app.route.createPilot           {0}').format(request.method))
    c_sub = ims.pilotSubscriber(sub)
    result = c_sub.subscriberCreate(session)
    if result.status_code == 500: #Successful EMA connection but there is an error.
        if result.text.find('Invalid Session') != -1:
            logger.debug(('** Leaving FUNC:::: app.route.createPilot:  Invalid Session'))
            return redirect(url_for('auth.login', error='Invalid Session'))
        elif result.text.find('already exists') != -1: # -1 means does not exist, therefore if True it exists.
            logger.debug(('** Leaving FUNC:::: app.route.createPilot:  Subscriber Already Exists'))
            session['mesg'] = 'ExistingSubscriber'
            return redirect(url_for('main.subscribers'))
        else:
            logger.debug('Unknown Error in createPilot func')
            pass
    elif result.status_code == 200:
        session['mesg'] = 'Created'
        session['sub'] = sub
        session['sub_pw'] = None
        del c_sub # Remove Subscriber Class instance
        logger.debug('** Leaving FUNC::::::: app.route.createPilot')
        return redirect(url_for('main.subscribers'))
    else:
        logger.debug(('** Leaving FUNC::::::: app.route.createPilot :::  Unknown Condition ::  {0}').format(result.status_code))
        return redirect(url_for('auth.login', error='Unknown error Condition'))
 

 
@main.route('/CreateRemoteWorker/<sub>' , methods=['POST','GET',])
@login_required
def createRW(sub):
    logger.debug(('FUNC:::::: app.route.createRW           {0}').format(request.method))
    c_sub = ims.remoteWorker(sub)
    result = c_sub.subscriberCreate(session)
    if result.status_code == 500: #Successful EMA connection but there is an error.
        if result.text.find('Invalid Session') != -1:
            logger.debug(('** Leaving FUNC:::: app.route.createRW:  Invalid Session'))
            return redirect(url_for('auth.login', error='Invalid Session'))
        elif result.text.find('already exists') != -1: # -1 means does not exist, therefore if True it exists.
            logger.debug(('** Leaving FUNC:::: app.route.createRW:  Subscriber Already Exists'))
            session['mesg'] = 'ExistingSubscriber'
            return redirect(url_for('main.subscribers'))
        elif result.text.find('Public Id must be SIP URI or TEL URL') != -1 or result.text.find('<ema:respCode>35012</ema:respCode>') != -1: # -1 means does not exist, therefore if True it exists.
            logger.debug('Subscription Not Created due to + missing or related error')
            flash ('Error')
            flash ('The Subscription Number did not start with a +')
            flash ('Please try again.....')
            session['mesg'] = 'No Plus'
            return redirect(url_for('main.subscribers'))
        else:
            logger.debug('Unknown Error in createRW func')
            flash('Unknown Error in createRW func')
            return redirect(url_for('main.subscribers'))
            
    elif result.status_code == 200:
        session['mesg'] = 'Created'
        session['sub'] = sub
        session['sub_pw'] = c_sub.password
        del c_sub # Remove Subscriber Class instance
        logger.debug('** Leaving FUNC::::::: app.route.createRW')
        return redirect(url_for('main.subscribers'))
    else:
        logger.debug(('** Leaving FUNC::::::: app.route.createRW :::  Unknown Condition ::  {0}').format(result.status_code))
        flash ('Unknown error Condition  Create RW')
        return redirect(url_for('auth.login', error='Unknown error Condition'))
 

@main.route('/CreateRangeNR/<sub>/<range>', methods=['POST','GET',])
@login_required
def createRangeNR(sub, range):
    logger.debug(('FUNC:::::: app.route.createRangeNR           {0}').format(request.method))
    session['rangesize'] = range
    session['sub_pw'] = None
    c_sub = ims.nonRegisteredRangeSubscriber(sub)
    c_sub.pubData.publicIdTelValue = c_sub.pubData.publicIdTelValue[:-4]  # Needed to remove !.*! for range xml
    result = c_sub.subscriberCreate(session)
    if result.status_code == 500: #Successful EMA connection but there is an error.
        if result.text.find('Invalid Session') != -1:
            logger.debug(('** Leaving FUNC:::: app.route.createRangeNR:  Invalid Session'))
            return redirect(url_for('auth.login', error='Invalid Session'))
        elif result.text.find('already exists') != -1: # -1 means does not exist, therefore if True it exists.
            logger.debug(('** Leaving FUNC:::: app.route.createRangeNR:  Subscriber Already Exists'))
            session['mesg'] = 'ExistingSubscriber'
            return redirect(url_for('main.subscribers'))
        elif result.text.find('Public Id must be SIP URI or TEL URL') != -1 or result.text.find('<ema:respCode>35011</ema:respCode>') != -1: # -1 means does not exist, therefore if True it exists.
            logger.debug('Unknown Error in app.route.createRangeNR')
            flash ('Error')
            flash ('The Subscription Number did not start with a +')
            flash ('Please try again.....')
            session['mesg'] = 'No Plus'
            return redirect(url_for('main.subscribers'))
            
        else:
            logger.debug('Unknown Error in createRangeNR func')
            flash ('Unknown Error')
            return redirect(url_for('main.subscribers'))
    elif result.status_code == 200:
        session['mesg'] = 'Created'
        session['sub'] = sub
        del c_sub # Remove Subscriber Class instance
        logger.debug('** Leaving FUNC::::::: app.route.createRangeNR')
        return redirect(url_for('main.subscribers'))
    else:
        logger.debug(('** Leaving FUNC::::::: app.route.createRangeNR :::  Unknown Condition ::  {0}').format(result.status_code))
        return redirect(url_for('auth.login', error='Unknown error Condition'))
 

@main.route('/CreateRangeR/<sub>/<range>' , methods=['POST','GET',])
@login_required
def createRangeR(sub, range):
    logger.debug(('FUNC:::::: app.route.createRangeR           {0}').format(request.method))
    session['rangesize'] = range
    c_sub = ims.registeredRangeSubscriber(sub)
    c_sub.pubData.publicIdTelValue = c_sub.pubData.publicIdTelValue[:-4]  # Needed to remove !.*! for range xml
    result = c_sub.subscriberCreate(session)
    if result.status_code == 500: #Successful EMA connection but there is an error.
        if result.text.find('Invalid Session') != -1:
            logger.debug(('** Leaving FUNC:::: app.route.createRangeR:  Invalid Session'))
            return redirect(url_for('auth.login', error='Invalid Session'))
        elif result.text.find('already exists') != -1: # -1 means does not exist, therefore if True it exists.
            logger.debug(('** Leaving FUNC:::: app.route.createRangeR:  Subscriber Already Exists'))
            session['mesg'] = 'ExistingSubscriber'
            return redirect(url_for('main.subscribers'))
            
        elif result.text.find('Public Id must be SIP URI or TEL URL') != -1 or result.text.find('<ema:respCode>35011</ema:respCode>') != -1: # -1 means does not exist, therefore if True it exists.
            logger.debug('Unknown Error in app.route.createRangeR')
            flash ('Error')
            flash ('The Subscription Number did not start with a +')
            flash ('Please try again.....')
            session['mesg'] = 'No Plus'
            return redirect(url_for('main.subscribers'))
        else:
            logger.debug('Unknown Error in app.route.createRangeR')
            pass
    elif result.status_code == 200:
        session['mesg'] = 'Created'
        session['sub'] = sub
        session['sub_pw'] = c_sub.password
        del c_sub # Remove Subscriber Class instance
        logger.debug('** Leaving FUNC::::::: app.route.createRangeR')
        return redirect(url_for('main.subscribers'))
        
    else:
        logger.debug(('** Leaving FUNC::::::: app.route.createRangeR :::  Unknown Condition ::  {0}').format(result.status_code))
        return redirect(url_for('auth.login', error='Unknown error Condition'))
        
#########################################################
##### DELETE
####################################################

@main.route('/delete', methods=['POST','GET',])
@login_required
def delete():
    logger.debug(('FUNC::::::: app.route.delete         {0}').format(request.method))
    if request.method == 'POST':
        logger.debug(request.form['submit'])
        sub = request.form['submit']
        cSub = ims.registeredSubscriber(sub) # For a delete any Class Type can work

        result = cSub.subscriberDelete(session)

        if result.status_code == 500: #Successful EMA connection but there is an error.
            if result.text.find('Invalid Session') !=(-1):
                logger.debug(('** Leaving FUNC::::::: app.route.delete::: Invalid Session::  {0}').format(result.status_code))
                logger.debug(('** Leaving FUNC::::::: app.route.delete:::  Invalid Session::  {0}').format(result.text))
                return redirect(url_for('auth.login', error='Invalid Session : Please login again.'))

            elif result.text.find('No such object') !=(-1):
                logger.debug(('** Leaving FUNC::::::: app.route.delete:::  No Such Object::  {0}').format(result.status_code))
                logger.debug(('** Leaving FUNC::::::: app.route.delete:::  No Such Object::  {0}').format(result.text))
                flash('Subscription does not exist!!')
                return redirect(url_for('main.searchRangeR'))
            else:
                logger.debug(('** Leaving FUNC::::::: app.route.delete:::  Unknown Condition ::  {0}').format(result.status_code))
                logger.debug(('** Leaving FUNC::::::: app.route.delete:::  Unknown Condition ::  {0}').format(result.text))
                session['mesg'] = ('Unknown Error:  {0}'.format(result.text))
                flash('Unknown Error has occurred, subscription not deleted. Contact Adminsitrator')
                return redirect(url_for('main.subscribers'))
                
        elif result.status_code == 200:
            logger.debug('** Leaving FUNC::::::: app.route.delete')
            session['mesg'] = 'Deleted'
            return redirect(url_for('main.subscribers'))

    else: #GET Method
        logger.debug('** Leaving FUNC::::::: app.route.delete')
        return render_template('searchRangeR.html', deletemesg = "True")
    return


####################################
### MISC
####################################
    
@main.route('/fraud', methods=['POST','GET',])
@login_required
def bw_ncos_check_apply():
    logger.debug(('FUNC:::::: app.route.fraud            ::: {0}').format(request.method))
    '''
    form = BWForm()
    
    if form.validate_on_submit():
        session['bwsub'] = request.form['bw_sub']
    '''
    session.permanent = True
    
    if request.method == 'POST':
        session['ncos_sub'] = str(request.form['ncos_sub'])
        sub = session['ncos_sub']
        if sub == "": 
            return redirect(url_for('main.subscribers'))
        
        logger.debug(('EXIT:::::: app.route.fraud    :: {1}        ::: {0}').format(request.method, session['ncos_sub']))
        return redirect(url_for(('main.bw_answer')))
    else:
        logger.debug(('EXIT:::::: app.route.fraud            ::: {0}').format(request.method))
        return render_template('ncosinput.html', ncos_sub = session.get('ncos_sub'))

    
@main.route('/bwanswer', methods=['POST','GET',])
@login_required        
def bw_answer():
    '''
        This function takes a sub number, retrieve the relevant information from BW.
        That will be the SUB, GROUP, ENTERPRISE.
    '''
    # Connect to BW
    if request.method == 'POST':
        logger.debug(('FUNC:::::: app.route.bwanswer ::: {1}           ::: {0}').format(request.method, str(request.form['ncos_sub'])))
        session.permanent = True
        session['ncos_sub'] = str(request.form['ncos_sub'])
        
        conn = mysockets.BWconnect()
        if (conn.isLiveNetwork()):
            logger.info('##LIVE ## Connecting to Live Broadworks Platform')
        
        if (conn.bwlogin()):
            xml = ocip.UserGetListInSystemRequest(conn.sessionid, session.get('ncos_sub')) # Create input XML
            result = conn.sendreceive(xml)    #Retrieve subscription information using UserGetListinSystem command
            
            tree = ET.fromstring(result)
            
            #Parse details and print in csv file
            #Method1
            rowlist = []
            datalist =[]
            #Using XML data, parse and extract the relevant information
            for elem in tree.getiterator():
                if(elem.tag == 'colHeading'):
                    rowlist.append(elem.text)
                elif (elem.tag == 'row'):
                    datalist.append(rowlist)
                    rowlist = []
                elif (elem.tag == 'col'):
                    rowlist.append(elem.text)
                else:
                    pass
            datalist.append(rowlist)
            
            #Method 2
            #Convert the XML data to Dicts and retrieve the relevant information from the dicts
            #Create a dict with headings, and then each entry can have the full subs details
            # Subs details are found in dict['BroadsoftDocument']['command']['userTable']['row']
            #Headinsg details are found in dict['BroadsoftDocument']['command']['userTable']['colHeading']
            d1 = xmltodict.parse(result)
            d2 = d1['BroadsoftDocument']['command']['userTable']['row']
            print (d1['BroadsoftDocument']['command']['userTable']['colHeading'])
            
            if isinstance(d2, list):
                for row in d2:
                    print (row.keys())
                    print (row.items())
            if isinstance(d2, dict):
                print (d2.keys())
                print (d2.items())
         
            #Prepare to show results screen
            if (datalist.__len__()):
                session['UserList'] =   datalist  
                session['userdict'] = d1
                conn.bwlogout()
                logger.debug(('EXIT:::::: app.route.bwanswer  ::: {1}            ::: {0}').format(request.method, session['ncos_sub']))
                return render_template('bwanswer.html', userlist = session.get('UserList'), userdict = session.get('userdict'))
            else:
                conn.bwlogout()
                logger.debug(('EXIT:::::: app.route.bwanswer  ::: {1}            ::: {0}').format(request.method, session['ncos_sub']))
                return render_template('ncosinput.html', ncos_sub = '')
                    
    else:#GET Request
         logger.debug(('FUNC:::::: app.route.bwanswer ::: {1}           ::: {0}').format(request.method))
        logger.debug(('EXIT:::::: app.route.bwanswer : NOT LOGGED IN           ::: {0}').format(request.method))
        return render_template('ncosinput.html', ncos_sub = '')
        
@main.route('/listSubscribers', methods=['POST','GET',])
@login_required
def listSubscribers():
    logger.debug(('FUNC:::::: app.route.listSubscribers                  :: {0}').format(request.method))
    logger.debug(request.method)
    if request.method == 'POST':
        logger.debug('** Leaving FUNC:::::: app.route.listSubscribersResults')
        return redirect(url_for ('main.listSubscribers'))
    else:
        logger.debug('** Leaving FUNC:::::: app.route.listSubscribers')
        return render_template('listSubscribers.html')

@main.route('/listSubscribersResults', methods=['POST','GET',])
@login_required
def listSubscribersResults():
    logger.debug(('FUNC:::::: app.route.listSubscribersResults                  :: {0}').format(request.method))
    logger.debug(request.method)
    if request.method == 'POST':
        logger.debug('** Leaving FUNC:::::: app.route.listSubscribersResults')
        
        result = checkLengthSubscriber(subscriber)
        
        return redirect(url_for ('main.listSubscribersResults'))
    else:
        logger.debug('** Leaving FUNC:::::: app.route.listSubscribersResults')
        return render_template('listSubscribersResults.html')


@main.route('/subscriberResult', methods=['POST','GET',])
@login_required
def subscriberResult():
    logger.debug(('FUNC:::::: app.route.subscriberResult                  :: {0}').format(request.method))
    logger.debug(request.method)
    if request.method == 'POST':
        logger.debug('** Leaving FUNC:::::: app.route.subscriberResult')
        return redirect(url_for ('main.subscriberResult'))
    else:
        logger.debug('** Leaving FUNC:::::: app.route.subscriberResult')
        return render_template('subscriberResult.html',count = session.get('count'), sub = session.get('sub'), details = session.get('details')) # Correct format to use Session Variables


@main.route('/subscribers', methods=['POST','GET',])
@login_required
def subscribers(mesg = None):
    logger.debug(('FUNC:::::: app.route.subscribers                ::{0}').format(request.method))
    if session.get('mesg'):        
        if session.get('mesg') == 'Deleted':
            logger.debug('** Leaving FUNC:::::: app.route.subscribers     ::  Subscriber Deleted')
            return render_template('subscribers.html', deletesub = session.get('sub'), deletemesg = 'Successful Delete')
        elif session.get('mesg') == 'NotProvisioned':
            logger.debug('** Leaving FUNC:::::: app.route.subscribers   ::  Subscriber not Provisioned')
            return render_template('subscribers.html', sub = session.get('sub'), mesg = 'Your Subscriber is not Provisioned')
        elif session.get('mesg') == 'Created':
            logger.debug('** Leaving FUNC:::::: app.route.subscribers    ::  Subscriber created')
            return render_template('subscribers.html', newsub = session.get('sub'), password = session.get('sub_pw'), createmesg = 'Your Subscriber has been Created')
        elif session.get('mesg') == 'ExistingSubscriber':
            logger.debug('** Leaving FUNC:::::: app.route.subscribers    ::  Subscriber Already Exists')
            return render_template('subscribers.html', existingsub = session.get('sub'), mesg = 'Your Subscriber already Exists')
        elif session.get('mesg') == 'No Plus':
            logger.debug('** Leaving FUNC:::::: app.route.subscribers    ::  No Plus')
            return render_template('subscribers.html', mesg = 'Please remember to add begin this subscriber type with a +')    
            
        else:
            logger.debug('** Leaving FUNC:::::: app.route.subscribers')
            return render_template('subscribers.html', mesg = mesg)
    else:
        logger.debug('** Leaving FUNC:::::: app.route.subscribers')
        return render_template('subscribers.html', mesg = mesg)

