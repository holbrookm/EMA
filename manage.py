#!/usr/bin/python

""" This script will be used to manage the the EMA APPlication start up etc
    #Marc Holbrook
    # 0851742253
    # <mholbrook@eircom.ie>
"""

import os
from datetime import timedelta
from app import create_app, db
from app.models import User, Role
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

manager = Manager(app)
migrate = Migrate(app, db) # Creating a Database Migration repository; use the python gui.py db init command

app.permanent_session_lifetime = timedelta(seconds = 600)  #  This entry forces a fresh session after 1 hour of inactivity.

###############################
#Manager Functions
def make_shell_context():
    return dict( app=app, db=db, User=User, Role=Role)
manager.add_command("shell", Shell(make_context = make_shell_context))
manager.add_command('db', MigrateCommand) 


@manager.command
def test():
    """ Run the unit tests. """
    import unittest2 
    tests = unittest2.TestLoader().discover('tests')
    unittest2.TextTestRunner(verbosity =2).run(tests)


if __name__ == '__main__':
    manager.run()
    



