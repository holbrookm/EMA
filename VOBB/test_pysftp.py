#!/usr/bin/python

import pysftp

ihost = '10.144.134.36'
iusername = 'root'
ipassword = 'root'

key_pass = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAIEArwDNasQJeYTlujxlf0Y1mXuUS4fmnTcBKNUSq7QVJ5wiL7KeomVcFJD7tLbgRq3VBGQ99cYiqPm5tFoxawwPJkSbZmQHcEdpJhUijfxUIYPunohk/O0JEEGmxii8va1t3ZoKU24xVNTS+zzrdQTXlmhni+MlhZpnO6DEZ2YI8qU='


srv = pysftp.Connection(host = ihost, username = iusername, password = ipassword, private_key_pass = key_pass)
print (srv.execute('ls -al'))

print ('I am in :)')

out = srv.execute('ipwcli   -user=admin -password=Root1290')
type(out)
print (out)
result = srv.execute('list enumdnsched 6.7.1.6.7.3.2.5.8.3.5.3.e164.arpa')
#print out
print result
srv.execute('exit')
srv.close()
