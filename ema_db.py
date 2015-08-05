#/usr/bin/python/

import logging_config
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String 
from sqlalchemy.sql import func
from datetime import datetime

#engine = create_engine('sqlite:///:memory:', echo=True)  # In memory DB

Base = declarative_base()



class EmaAccess(Base):     
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
    



def initdb():
    """"""
    logger.debug('FUNC: ema_db.initdb()   :')
    if debug.mac():
        engine = create_engine('sqlite:///test_ema.db', echo=True)
    else:
        engine = create_engine('sqlite:///ema.db', echo=True)        
    db = Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    logger.debug('**Leaving:: FUNC: ema_db.initdb()   :'
    return session

