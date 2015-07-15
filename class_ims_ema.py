#!/usr/bin/python

""" This script will access the EMA via http commands with SOAP XML content.
    #Marc Holbrook
    # 0851742253
    # <mholbrook@eircom.ie>
"""

import debug
import requests
import ema_functions as ema

from abc import ABCMeta, abstractmethod

class IMSSubscriber(object):

    __metaclass__ = ABCMeta
    origProfileId = 'siptrunk_orig_invite_reg_retail'
    termProfileId = 'siptrunk_term_invite_reg_retail'


    def __init__(self, number = '9999999999'):
        """
        : attribute subscriberId: string
        : attribute subscriberProfId : string
        : attribute defaultPrivateId : string
        : attribute allow_tags : bool
        : attribute attributes : array
        """
        plus = '+'
        suffix = '@ngv.eircom.net'
        FALSE = 'FALSE'
        TRUE = 'TRUE'
        sip = 'sip:'
        
        self.subscriberId = plus + number + suffix
        self.subscriberBarringInd = FALSE
        self.chargingProfId = number
        self.privacyIndicator = FALSE
        self.defaultPrivateId = self.subscriberId
        self.pubData = pubData(number, self.origProfileId, self.termProfileId)
        self.privateUser = privateUser(self.subscriberId)
        
    def subscriberCreate(self, session):
        """ This function will delete the subscriber with EMA to the HSS and ENUM.
        """
        debug.p('FUNC:: Class IMSSubscriber.subscriberCreate(self, session)             ')
        
        status = ema.emaCreateImsSubscriber( self, session )
        debug.p('**Leaving FUNC :::: class_ims_ema.subscriberCreate')
        return status
        
    def subscriberDelete(self, session):
        """ This function will delete the subscriber with EMA to the HSS and ENUM.
        """
        debug.p('FUNC:: Class IMSSubscriber.subscriberDelete(self, session)             ')
        
        status = ema.emaDeleteImsSubscriber( self, session)
        debug.p('**Leaving FUNC :::: class_ims_ema.subscriberDelete')
        return status
    
    def subscriberGet(self, session):
        """ This function will search for the subscriber with EMA in the HSS and ENUM.
        """
        debug.p('FUNC:: Class IMSSubscriber.subscriberGet(self, session)             ')
        
        status = ema.emaGetImsSubscriber( self, session )
        debug.p('**Leaving FUNC :::: class_ims_ema.subscriberGet')
        return status   
    
    @abstractmethod
    def subscriberType(self):
        """ Return a string representing the type of subscriber this is."""
        pass
       
        
class pubData(object):

    def __init__(self, number, orig, term):
        """
        : attribute id : string
        : attribute value : string
        """

        FALSE = 'FALSE'
        TRUE = 'TRUE'
        plus = '+'
        suffix = '@ngv.eircom.net'
        FALSE = 'FALSE'
        TRUE = 'TRUE'
        sip = 'sip:'
        tel = 'tel:'
        self.subscriberId = plus + number + suffix
        
        self.publicIdValue = sip + self.subscriberId
        self.privateUserId = self.subscriberId
        self.publicIdState = 'not_registered'
        self.publicIdTelValue = tel + plus + number
        self.subscriberServiceProfileId = self.subscriberId
        self.xcapAllowed = FALSE
        self.implicitRegSet = 1
        self.isDefault = TRUE
        self.sessionBarringInd = FALSE
        self.maxNumberOfContacts = 5
        self.configuredServiceProfile1= configuredServiceProfile(orig)
        self.configuredServiceProfile2= configuredServiceProfile(term)
        self.maxSessions = 100
        self.phoneContext = None
        
        return

class configuredServiceProfile(object):
    def __init__(self, profile):
        """
        : attribute profile : string
        
        """
        self.configuredServiceProfileId = profile
        return        

class privateUser(object):
    def __init__(self, subscriberId):
        """
        : attribute id : string
        : attribute value : string
        """
        FALSE = 'FALSE'
        TRUE = 'TRUE'

        
        self.subscriberId = subscriberId
        self.privateUserId = self.subscriberId
        self.userState = 'not_registered'
        self.userBarringInd  = FALSE
        self.roamingAllowed = FALSE
        self.allowedAuthMechanism = 'Digest'
        self.sipLocked = FALSE
        return
        
def jdefault(o):
    if isinstance(o, MexSubscription):
        return o.__dict__
    elif isinstance(o, Attributes):
        return o.__dict__

class nonRegisteredSubscriber(IMSSubscriber):
    """ This calls should represent a non Registered Subscriber. """

    origProfileId = 'siptrunk_orig_invite_non_reg_retail'
    termProfileId = 'siptrunk_term_invite_non_reg_retail'
    
    def subscriberType(self):
        return 'Non Registered Subscriber'

class registeredSubscriber(IMSSubscriber):
    """ This calls should represent a Registered Subscriber. """

    origProfileId = 'siptrunk_orig_invite_reg_retail'
    termProfileId = 'siptrunk_term_invite_reg_retail'

    def subscriberType(self):
        return 'Registered Subscriber'

class nonRegisteredRangeSubscriber(IMSSubscriber):
    """ This calls should represent a non Registered Range Subscriber. """

    origProfileId = 'siptrunk_orig_invite_non_reg_retail'
    termProfileId = 'siptrunk_term_invite_non_reg_retail'

    def subscriberType(self):
        return 'Non Registered Range Subscriber'

class registeredRangeSubscriber(IMSSubscriber):
    """ This calls should represent a Registered Range Subscriber. """

    origProfileId = 'siptrunk_orig_invite_reg_retail'
    termProfileId = 'siptrunk_term_invite_reg_retail'

    def subscriberType(self):
        return 'Registered Range Subscriber'


