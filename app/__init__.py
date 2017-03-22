#!/usr/bin/python

""" This script will access the EMA via http commands with SOAP XML content.
    #Marc Holbrook
    # 0851742253
    # <mholbrook@eircom.ie>
"""
import logging_config

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.bootstrap import Bootstrap
from config import config

db = SQLAlchemy()
bootstrap = Bootstrap()

logger = logging_config.logger

###############################
# Login Manager Set Up
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

def create_app(config_name):
    logger.debug('FUNC::::::: app.__init__.create_app()')
        
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    login_manager.init_app(app) 
    db.init_app(app)        # Initialises the DB used for usernames/passwords.
    bootstrap.init_app(app) #Initialises the bootstrap module for the HTML 
    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix ='/auth')
    
    logger.debug('** Leaving FUNC::::::: app.__init__.create_app()')
    return app
    
    



