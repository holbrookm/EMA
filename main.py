#!/usr/bin/python

""" This script will try and access the EMA via http commands with SOAP XML content.
    #Marc Holbrook
    # 0851742253
    # <mholbrook@eircom.ie>
"""

import ema_functions as ema
#import xml.etree.ElementTree as ET
from lxml import etree as ET
import xmltodict, json
#import class_ims_ema as ims
import class_ema_ims as ims

def pack_dict(tree):
    """ This function will take an lxml.tree element as an input and parse through the element. 
        The outcome should be a list off all the subscription elements which will be fed in a class.
    """
    d = {}
    for node in tree.getiterator():
        x, y = node.tag.split('}')
        if node.tag.startswith('{http://schemas.ericsson.com/ema/UserProvisioning/IMS/5.0/'):
            d[y] = node.text
    return d




sequence_id, session_id = ema.ema_login('sogadm', 'sogadm')

subscription_id = '+353766875239@ngv.eircom.net'

sub_xml = ema.ema_get_ims_subscription(sequence_id, session_id, '123456', subscription_id)

print(type(sub_xml))

root =ET.fromstring(sub_xml)

for node in root.getiterator():
    print node.tag,(':::'),  node.text


print root.items()

print root.keys()

print (len(root))

for child in root:
    print child.tag
    print child.text
    print len(child)
    for x in child:
        print x.tag, x.text, len(x)


class imsSubscription(dict):
    def __init__(self, dictionary):
        for k,v in dictionary.items():
            setattr(self, k, v)

class imsSubscriber(dict):
    def __init__(self, *arg, **kw):
        super(imsSubscriber,self).__init__(*arg, **kw)



d ={}

d = pack_dict(root)
print d.keys()
print d.values()


c1= imsSubscription(d)

print c1.subscriberId

e1 = xmltodict.parse(sub_xml)
e2 =  e1['S:Envelope']['S:Body']['GetResponse']['MOAttributes']['getResponseIMSSubscription']

e3 = imsSubscriber(e2)

for k,v in e3.items():
    print k, '::::      ', v
#ema.ema_logout(session_id)

ub1 = ema.prepareXmlToClass(sub_xml)

ub2 = ims.imsSubscriber(ub1)

print (ub2)

"""

m = ims.IMSSubscriber('353876167960')

print m
"""
print 'JSONJSONJSONJSON\n\n'
print(json.dumps(e1))
print 'JSONJSONJSONJSON\n\n'
json.dumps(e2)
print 'JSONJSONJSONJSON\n\n'
json.dumps(e3)