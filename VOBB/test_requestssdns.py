#!/usr/bin/python

import requests
import pysftp

ihost = '10.144.134.36'
iusername = 'root'
ipassword = 'root'

key_pass = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAIEArwDNasQJeYTlujxlf0Y1mXuUS4fmnTcBKNUSq7QVJ5wiL7KeomVcFJD7tLbgRq3VBGQ99cYiqPm5tFoxawwPJkSbZmQHcEdpJhUijfxUIYPunohk/O0JEEGmxii8va1t3ZoKU24xVNTS+zzrdQTXlmhni+MlhZnO6DEZ2YI8qU='


srv = pysftp.Connection(host = ihost, username = iusername, password = ipassword, private_key_pass = key_pass)
print (srv.execute('ls -al'))

print ('I am in :)')

#REQUEST SPECIFIC
user = 'admin'
pwd = 'Root1290'

login_url = 'http://10.144.134.36:8080/ipworks/webapp/login'
_headers = {'content-type':'text/html'}
r = requests.post (login_url, headers = _headers, auth = (user, pwd))
print r.status_code
print r.text






