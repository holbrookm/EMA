#!/usr/bin/python

""" This script will access the EMA via http commands with SOAP XML content.
    #Marc Holbrook
    # 0851742253
    # <mholbrook@eircom.ie>
"""

import class_ims_ema as ims


def checkSessionSubType(session):
    """ This method should return the Subscriber class instance for the current session instructions.
    """
    if session['subType'] == 'registeredRangeSubscriber':
		cSub = ims.registeredRangeSubscriber(session['sub'])
    elif session['subType'] == 'nonRegisteredRangeSubscriber':
        cSub = ims.nonRegisteredRangeSubscriber(session['sub'])
    elif session['subType'] == 'registeredSubscriber':
        cSub = ims.registeredSubscriber(session['sub'])
    elif session['subType'] == 'nonRegisteredSubscriber':
        cSub = ims.nonRegisteredSubscriber(session['sub'])
    else:
        pass
    return cSub


def setSessionSubType(subType):
    """ This method should return the Subscriber class instance for the current session instructions.
    """

    types {'1': 'registeredRangeSubscriber', '2': 'nonRegisteredRangeSubscriber', '3': 'registeredSubscriber', '4': 'nonRegisteredSubscriber'}
    if types[subType] == 'registeredRangeSubscriber':
        cSub = ims.registeredRangeSubscriber(session['sub'])
    elif types[subType] == 'nonRegisteredRangeSubscriber':
        cSub = ims.nonRegisteredRangeSubscriber(session['sub'])
    elif types[subType] == 'registeredSubscriber':
        cSub = ims.registeredSubscriber(session['sub'])
    elif types[subType] == 'nonRegisteredSubscriber':
        cSub = ims.nonRegisteredSubscriber(session['sub'])
    else:
        pass
    return cSub



