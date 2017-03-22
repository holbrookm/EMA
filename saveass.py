#more debug.log.1  |grep ' ::::: Session Id 1 :' |awk -F" " '{print $19}' > sess.log
import sys
import subprocess
import csv
import ema_functions as ema
inputlist = []

filename = './debug.log'

commandstring = (''' cat %s |grep ' ::::: Session Id 1 :' |awk -F" " '{print $19}' > sess.log ''' %(filename))

print ('Looking for  {0}\n\n'.format(filename))


p1 = subprocess.Popen("cat %s" %filename, shell = True, stdout = subprocess.PIPE)
grep = subprocess.Popen(("grep ' ::::: Session Id 1 :'"), shell = True, stdin = p1.stdout, stdout =subprocess.PIPE)
p1.stdout.close()
awk = subprocess.Popen(('''awk -F " " '{print $19}' '''), shell = True, stdin = grep.stdout, stdout = subprocess.PIPE)
grep.stdout.close()

ses_list = awk.stdout.read()
print(type(ses_list))
for entry in ses_list.split('\n'):
    if entry != '':
        #ema.ema_logout(entry)
        inputlist.append(entry)

print (" File Exists. It has ", len(inputlist), " number of entries" )
print ses_list
awk.stdout.close()

# SECOND METHOD OF USING SUBPROCESS
'''
if (subprocess.Popen(commandstring, shell = True)) == 0:
    print('ERROR with linux parsing log call!!!')
    sys.exit()
with open('sess.log','ra') as fin:
    reader = csv.reader(fin)
    for row in reader:
        if row[0]!= '':
            #ema.ema_logout(row[0])
            inputlist.append(row)
print (" File Exists. It has ", len(inputlist), " number of entries" )  

print inputlist

'''
