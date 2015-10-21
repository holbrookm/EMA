#!/usr/bin/python

""" This script will access the EMA via http commands with SOAP XML content.
    #Marc Holbrook
    # 0851742253
    # <mholbrook@eircom.ie>
"""

import debug
import logging_config
import requests
import ema_functions as ema
import m_password

from abc import ABCMeta, abstractmethod

logger = logging_config.logger

class IMSSubscriber(object):

    __metaclass__ = ABCMeta
    origProfileId = 'siptrunk_orig_invite_reg_retail'
    termProfileId = 'siptrunk_term_invite_reg_retail'
    charge = 'DefaultChargingProfile'
    domain = '@ngv.eircom.net'

    def __init__(self, number):
        """
        : attribute subscriberId: string
        : attribute subscriberProfId : string
        : attribute defaultPrivateId : string
        : attribute allow_tags : bool
        : attribute attributes : array
        """
        
        FALSE = 'FALSE'
        TRUE = 'TRUE'
        sip = 'sip:'
        
        self.subscriberId =  number + self.domain
        self.subscriberBarringInd = FALSE
        self.chargingProfId = self.charge
        self.privacyIndicator = FALSE
        self.defaultPrivateId = self.subscriberId
        self.pubData = pubData(number,self.domain, self.origProfileId, self.termProfileId)
        self.privateUser = privateUser(self.subscriberId)
        self.phoneNumber =  number
        self.password = m_password.id_generator(8)
        
        # Not Needed for Fixed Line:::::    self.msisdn = number # added in to cater for Charging Profile, Msisdn exists in PrivateData
        
    def subscriberCreate(self, session):
        """ This function will delete the subscriber with EMA to the HSS and ENUM.
        """
        logger.debug('FUNC:: Class IMSSubscriber.subscriberCreate(self, session)             ')
        if self.charge == 'HostedOfficeChargingProfile':
            status = ema.emaCreateHOSubscriber( self, session )
        elif self.subscriberType() == 'Remote Worker':
            status = ema.emaCreateRWSubscriber(self, session)
        elif self.subscriberType() == 'Pilot Subscriber':
            status = ema.emaCreateRegisteredPBXPilotNumber(self, session)
        else:
            status = ema.emaCreateImsSubscriber( self, session )
        logger.debug('**Leaving FUNC :::: class_ims_ema.subscriberCreate')
        return status
        
    def subscriberDelete(self, session):
        """ This function will delete the subscriber with EMA to the HSS and ENUM.
        """
        logger.debug('FUNC:: Class IMSSubscriber.subscriberDelete(self, session)             ')
        
        status = ema.emaDeleteImsSubscriber( self, session)
        logger.debug('**Leaving FUNC :::: class_ims_ema.subscriberDelete')
        return status
    
    def subscriberGet(self, session):
        """ This function will search for the subscriber with EMA in the HSS and ENUM.
        """
        logger.debug('FUNC:: Class IMSSubscriber.subscriberGet(self, session)             ')
        
        status = ema.emaGetImsSubscriber( self, session )
        logger.debug('**Leaving FUNC :::: class_ims_ema.subscriberGet')
        return status   
    
    @abstractmethod
    def subscriberType(self):
        """ Return a string representing the type of subscriber this is."""
        pass
       
        
class pubData(object):

    def __init__(self, number, domain, orig, term):
        """
        : attribute id : string
        : attribute value : string
        """

        FALSE = 'FALSE'
        TRUE = 'TRUE'
        plus = '+'
        FALSE = 'FALSE'
        TRUE = 'TRUE'
        sip = 'sip:'
        tel = 'tel:'
        self.subscriberId =  number + domain
        
        self.publicIdValue = sip + self.subscriberId
        self.privateUserId = self.subscriberId
        self.publicIdState = 'not_registered'
        self.publicIdTelValue = tel +  number
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

class remoteWorker(IMSSubscriber):
    """ This calls should represent a Registered Subscriber. """

    origProfileId = 'siptrunk_orig_invite_reg_retail'
    termProfileId = 'siptrunk_term_invite_reg_retail'

    def subscriberType(self):
        return 'Remote Worker'        

class pilotSubscriber(IMSSubscriber):
    """ This calls should represent a Registered Subscriber. """

    origProfileId = 'siptrunk_orig_invite_reg_retail'
    termProfileId = None

    def subscriberType(self):
        return 'Pilot Subscriber'         
        
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

class hostedOfficeSubscriber(IMSSubscriber):
    """ This calls should represent a Registered Range Subscriber. """

    origProfileId = 'ho_orig_retail'
    termProfileId = 'ho_term_retail'
    charge = 'HostedOfficeChargingProfile'

    def subscriberType(self):
        return 'Hosted Office Subscriber'

