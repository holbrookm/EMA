#!/usr/bin/python

""" This script is a Blueprint  which defines routes for Flask Applications.

    (Chapter 7 pg 79)
    #Marc Holbrook
    # 0851742253
    # <mholbrook@eircom.ie>
"""

from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
