#!/usr/bin/python
import dns.resolver

myDNS = dns.resolver.Resolver()
#myDNS.nameservers = ['10.144.132.8']
myDNS.nameservers = ['10.144.134.20']
myAnswer = myDNS.query('6.7.1.6.7.3.2.5.8.3.5.3.e164.arpa','NAPTR')
type(myAnswer)
print myAnswer.response

