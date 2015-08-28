#!/usr/bin/python

""" This script will provide the intelligence for the login forms and authentication forms.
    #Marc Holbrook
    # 0851742253
    # <mholbrook@eircom.ie>
"""

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Email, Length

class LoginForm(Form):
    username = StringField('Username', validators = [Required(), Length(1,64)])
    password = PasswordField('Password', validators = [Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')
    
    