#!/usr/bin/python
""" This script will access the EMA via http commands with SOAP XML content.
    #Marc Holbrook
    # 0851742253
    # <mholbrook@eircom.ie>
"""
from flask import render_template, session, redirect, url_for, request, flash
from flask.ext.login import login_user, logout_user, login_required
from .forms import LoginForm

from .. import db

from flask import render_template, session, redirect, url_for, request, flash
from flask.ext.login import login_user, logout_user, login_required
from .forms import LoginForm

from .. import db
#from .. import logger
from ..models import User
from . import auth

from logging_config import logger
import class_ims_ema as ims
import ema_functions as ema

import debug

@auth.route('/')
def index():
    """ Index Page.
    """
    logger.debug('FUNC::::::: app.auth.route.index')
    logger.debug('** Leaving FUNC::::::: app.auth.route.index')
    form = LoginForm ()
    return render_template('auth/login.html', form = form)



@auth.route('/login', methods=['POST', 'GET',])
def login(error = None):
    logger.debug(('FUNC::::::: auth.route.login::: request Method is ::' + request.method))
    
    form = LoginForm()
    #if request.method == 'POST':
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
    logger.debug('** Leaving FUNC::::::: app.route.login')
    return render_template('auth/login.html', form = form)
    
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))
    
    
