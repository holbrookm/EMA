#!/usr/bin/python
import sys, os
from flask import Flask, request, render_template, url_for, redirect, flash, session, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.login import login_user, logout_user, login_required
from .forms import LoginForm

from config import config

import debug, logging_config
import class_ims_ema as ims
import ema_functions as ema
import session_calls

#Blueprint required imports
from . import main
from .. import db
from ..models import User



logger = logging_config.logger
################################

@main.route('/',  methods=['POST','GET',])
def index():
    """ Index Page.
    """
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
            session['transaction_id'] = '2222222'
            return redirect(url_for(('main.subscribers')))
        flash('Invalid Username and Password')
    
    logger.debug('** Leaving FUNC::::::: app.main.route.index')
    return render_template('/login.html', form = form)   # I believe that this is the first function/view called


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
    logger.debug(('FUNC:::::: app.route.performSearchRangeR           {0}').format(request.method))
    
    if request.method == 'POST':
        sub = str(request.form['sub'])
        session['sub'] = sub   # subscriber number in text
        c_sub = ims.registeredRangeSubscriber(sub)
        transaction_id = session['transaction_id']
        result = c_sub.subscriberGet(session['emaSession'])
        logger.debug (result.status_code)
        logger.debug (result.text)

        if result.status_code == 500: #Successful EMA connection but there is an error.
            if result.text.find('Invalid Session') != -1:
                logger.debug(('** Leaving FUNC:::: app.route.performSearchrangeR:  Invalid Session'))
                return redirect(url_for('main.login', error='Invalid Session'))
            elif result.text.find('No such object') != -1:
                logger.debug(('** Leaving FUNC:::: app.route.performSearchrangeR:  Subscriber not provisioned: redirecting to subscribers.html'))
                session['mesg'] = 'NotProvisioned'
                return redirect(url_for('main.subscribers'))
            else:
                pass
        if result.status_code == 200:
            subdetails = ema.prepareXmlToClass(result.text)
            session['subType'] = subdetails['pubData']['publicIdState'] # Current Subscriber State in text
            session['details'] = subdetails  # Current Subscriber SOAP XML structure

            del c_sub # Remove Subscriber Class instance

            logger.debug('**Leaving FUNC:::::: app.route.performSearchRangeR: Status = 200')
            return redirect(url_for('main.subscriberResult'))
            
    else:
        return render_template('/login.html')
        logger.error('Unexpected error occurred in app.route.performSearchRangeR ')
    logger.debug('** Leaving FUNC::::::: app.route.performSearchRangeR: End of Func error')
    return render_template('/login.html')


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
    result = c_sub.subscriberCreate(session['emaSession'])
    
    if result.status_code == 500: #Successful EMA connection but there is an error.
        if result.text.find('Invalid Session') != -1:# -1 means does not exist, therefore if True it exists.
            logger.debug(('** Leaving FUNC:::: app.route.createNR:  Invalid Session'))
            return redirect(url_for('main.login', error='Invalid Session'))
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
        return redirect(url_for('main.login', error='Unknown error Condition'))
 

@main.route('/CreateRangeNR/<sub>', methods=['POST','GET',])
@login_required
def createRangeNR(sub):
    logger.debug(('FUNC:::::: app.route.createRangeNR           {0}').format(request.method))
    c_sub = ims.nonRegisteredRangeSubscriber(sub)
    result = c_sub.subscriberCreate(session['emaSession'])
    if result.status_code == 500: #Successful EMA connection but there is an error.
        if result.text.find('Invalid Session') != -1:
            logger.debug(('** Leaving FUNC:::: app.route.createRangeNR:  Invalid Session'))
            return redirect(url_for('main.login', error='Invalid Session'))
        elif result.text.find('already exists') != -1: # -1 means does not exist, therefore if True it exists.
            logger.debug(('** Leaving FUNC:::: app.route.createRangeNR:  Subscriber Already Exists'))
            session['mesg'] = 'ExistingSubscriber'
            return redirect(url_for('main.subscribers'))
        else:
            logger.debug('Unknown Error in createRangeNR func')
            pass
    elif result.status_code == 200:
        session['mesg'] = 'Created'
        session['sub'] = sub
        del c_sub # Remove Subscriber Class instance
        logger.debug('** Leaving FUNC::::::: app.route.createRangeNR')
        return redirect(url_for('main.subscribers'))
    else:
        logger.debug(('** Leaving FUNC::::::: app.route.createRangeNR :::  Unknown Condition ::  {0}').format(result.status_code))
        return redirect(url_for('main.login', error='Unknown error Condition'))
 


@main.route('/CreateR/<sub>', methods=['POST','GET',])
@login_required
def createR(sub):
    logger.debug(('FUNC:::::: app.route.createR           {0}').format(request.method))
    c_sub = ims.registeredSubscriber(sub)# Create Registered Subscriber Class instance
    result = c_sub.subscriberCreate(session['emaSession'])
   
    if result.status_code == 500: #Successful EMA connection but there is an error.
        if result.text.find('Invalid Session') != -1:
            logger.debug(('** Leaving FUNC:::: app.route.createR:  Invalid Session'))
            return redirect(url_for('main.login', error='Invalid Session'))
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

@main.route('/CreateRangeR/<sub>' , methods=['POST','GET',])
@login_required
def createRangeR(sub):
    logger.debug(('FUNC:::::: app.route.createRangeR           {0}').format(request.method))
    c_sub = ims.registeredRangeSubscriber(sub)
    result = c_sub.subscriberCreate(session['emaSession'])
    if result.status_code == 500: #Successful EMA connection but there is an error.
        if result.text.find('Invalid Session') != -1:
            logger.debug(('** Leaving FUNC:::: app.route.createRangeR:  Invalid Session'))
            return redirect(url_for('main.login', error='Invalid Session'))
        elif result.text.find('already exists') != -1: # -1 means does not exist, therefore if True it exists.
            logger.debug(('** Leaving FUNC:::: app.route.createRangeR:  Subscriber Already Exists'))
            session['mesg'] = 'ExistingSubscriber'
            return redirect(url_for('main.subscribers'))
        else:
            logger.debug('Unknown Error in createRangeR func')
            pass
    elif result.status_code == 200:
        session['mesg'] = 'Created'
        session['sub'] = sub
        del c_sub # Remove Subscriber Class instance
        logger.debug('** Leaving FUNC::::::: app.route.createRangeR')
        return redirect(url_for('main.subscribers'))
    else:
        logger.debug(('** Leaving FUNC::::::: app.route.createRangeR :::  Unknown Condition ::  {0}').format(result.status_code))
        return redirect(url_for('main.login', error='Unknown error Condition'))
 



#########################################################
##### DELETE
####################################################

@main.route('/delete', methods=['POST','GET',])
@login_required
def delete():
    #
    #
    logger.debug(('FUNC::::::: app.route.delete         {0}').format(request.method))
    if request.method == 'POST':
        logger.debug(request.form['submit'])
        sub = request.form['submit']
        cSub = ims.registeredSubscriber(sub) # For a delete any Class Type can work

        result = cSub.subscriberDelete(session['emaSession'])

        if result.status_code == 500: #Successful EMA connection but there is an error.
            if result.text.find('Invalid Session'):
                logger.debug('********Invalid Session')
                return redirect(url_for('main.login', error='Invalid Session : Please login again.'))
            elif result.text.find('No such object'):
                logger.debug('******** No Such object')
                return redirect(url_for('main.searchRangeR'))
            else:
                pass
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
        return render_template('subscriberResult.html', sub = session.get('sub'), details = session.get('details')) # Correct format to use Session Variables


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
            return render_template('subscribers.html', newsub = session.get('sub'), createmesg = 'Your Subscriber has been Created')
        elif session.get('mesg') == 'ExistingSubscriber':
            logger.debug('** Leaving FUNC:::::: app.route.subscribers    ::  Subscriber Already Exists')
            return render_template('subscribers.html', existingsub = session.get('sub'), mesg = 'Your Subscriber already Exists')
        else:
            logger.debug('** Leaving FUNC:::::: app.route.subscribers')
            return render_template('subscribers.html', mesg = mesg)
    else:
        logger.debug('** Leaving FUNC:::::: app.route.subscribers')
        return render_template('subscribers.html', mesg = mesg)

