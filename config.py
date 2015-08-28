#!/usr/bin/python

""" This script will be the configuration file for the EMA APPlication.
    #Marc Holbrook
    # 0851742253
    # <mholbrook@eircom.ie>
"""

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'developmentkey'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    
    @staticmethod
    def init_app(app):
        pass
        

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATEBASE_URL') or 'sqlite:///' + os.path.join(basedir, 'emagui.db')
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATEBASE_URL') or 'sqlite:///' + os.path.join(basedir, 'emagui.db')
    

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATEBASE_URL') or 'sqlite:///' + os.path.join(basedir, 'ProductionEMAGUI.db')
    
config = {
    'development' : DevelopmentConfig,
    'testing' : DevelopmentConfig,
    'production' : ProductionConfig,
    'default' : DevelopmentConfig
}
    
