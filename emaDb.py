#/usr/bin/python/

import logging_config
from datetime import datetime

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

class EmaAccess(db.Model):     
    __tablename__ = 'EmaAccess'
    #__table_args__ = {'autoload':True}
    id = Column(Integer, primary_key=True)
    user = Column(String)
    password = Column(String)
    date = Column(String)
    
    def __init__(self, user, password):
        logger.debug('FUNC: ema_db.EmaAccess.__init__()   :')
        self.user = user
        self.password = password
        self.date = datetime.datetime.now()
        logger.debug('**Leaving :: FUNC: ema_db.EmaAccess.__init__()   :')
        return
        
    def __repr__(self):
        return ("<EmaAccess(User='%s',Password='%s', Date='%s')>" % (self.User, self.Password, self.Date))
    




