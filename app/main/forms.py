#!/usr/bin/python

""" This script will provide the intelligence for the login forms and authentication forms.
    #Marc Holbrook
    # 0851742253
    # <mholbrook@eircom.ie>
"""

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(Form):
    username = StringField('Username', validators = [DataRequired(), Length(1,64)])
    password = PasswordField('Password', validators = [DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')
    
    
class BWForm(Form):
    bw_sub = StringField('Broadworks Subscriber', validators = [DataRequired(), Length(1,10)])
    search = SubmitField('Search')