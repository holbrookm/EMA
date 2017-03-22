#more debug.log.1  |grep ' ::::: Session Id 1 :' |awk -F" " '{print $19}' > sess.log

import csv
import ema_functions as ema
inputlist = []
with open('sess.log','ra') as fin:
    reader = csv.reader(fin)
    for row in reader:
        if row[0]!= '':
            ema.ema_logout(row[0])
            inputlist.append(row)
print (" File Exists. It has ", len(inputlist), " number of entries" )  
