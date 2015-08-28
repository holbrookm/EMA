#!/usr/bin/python

import sys, string, logging, os

try:
  os.remove('./ema_prov.log')
except:
  pass

#logging levels:
CRITICAL=50
ERROR=40
WARNING=30
NOTICE=25
INFO=20
INFO1=15
DEBUG=10
DEBUG1=5


FILE_LEVEL=DEBUG
CONSOLE_LEVEL=DEBUG

#FORMAT = "%(levelname)s l: %(lineno)d: %(message)s"
#FORMAT = "%(levelname)s | %(module)s |  %(message)s"
#logging.basicConfig(format=FORMAT)
#FORMAT = "%(levelname)s | %(module)s | %(name)s | %(message)s"
#logging.basicConfig(format=FORMAT)

# Format of the log entry
FORMAT = "%(asctime)s %(levelname)s | %(module)s | %(name)s | %(message)s"

logging.basicConfig(filename='./debug.log',format=FORMAT)
logging.addLevelName(15, "INFO1")
logging.addLevelName(5, "DEBUG1")
logging.addLevelName(25, "NOTICE")

console = logging.StreamHandler() # Console Logging Entry
console.setLevel( CONSOLE_LEVEL ) # Set console logging level as level set above
formatter =logging.Formatter(FORMAT) # Sets formatter to format specified above
console.setFormatter( formatter ) # Adds formatter to the console Logging Entry 
logging.getLogger('').addHandler(console)  # Adds the console log to the file log

logger = logging.getLogger() # Instance of log (both file and console as console is added) is now set to logger
logger.setLevel( FILE_LEVEL ) # Sets File Log Level as level for Logger/ remember Console level is already set
