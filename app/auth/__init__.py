#!/usr/bin/python

from flask import Blueprint

from logging_config import logger

logger.debug('FUNC::::::: app.auth.__init__')

auth = Blueprint('auth', __name__)

from . import views

logger.debug('**Leaving FUNC::::::: app.auth.__init__')
