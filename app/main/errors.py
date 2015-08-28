#!/usr/bin/python

""" This script is the error file required with the view file.
    This is a Blueprint with Error handlers
    (Chapter 7 pg 80)
    #Marc Holbrook
    # 0851742253
    # <mholbrook@eircom.ie>
"""


from flask import render_template

from . import main

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
