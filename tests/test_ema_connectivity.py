#!/usr/bin/python

""" This script will access the EMA via http commands with SOAP XML content.
    #Marc Holbrook
    # 0851742253
    # <mholbrook@eircom.ie>
"""
import sys
sys.path.append('/home/ema-gui/emagui2/')
import unittest2
import ema_functions
import class_ims_ema

class EMAConnectivityTestCase(unittest2.TestCase):
      
    def test_is_ims_sub_activities(self):
        """ test is to return True if IMS sub is created. """
        emaSession = ema_functions.emaLogin()
        session = {}
        session['emaSession'] = emaSession
        sub1 = class_ims_ema.remoteWorker('+353760000001')
        test1 = sub1.subscriberCreate(session)
        test2 = sub1.subscriberGet(session)
        test3 = sub1.subscriberDelete(session)
        test4 = sub1.subscriberGet(session)
        self.assertTrue(test1.status_code == 200 and test2.status_code == 200 and test3.status_code == 200 and test4.status_code == 500)
        
   
    
if __name__ == '__main__':
    unittest2.main()        
