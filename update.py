import sys
import os.path
import os
import re

print "Updating Python Modules"
print "Updating python-dateutil"
os.system("sudo pip install python-dateutil --upgrade")
print "Updating tzlocal"
os.system("sudo pip install tzlocal --upgrade")
print "Updating python-metar"
os.system("sudo pip install python-metar --upgrade")

buttonFileName = 'Button/gpio-keys'
print "Checking " + buttonFileName
if os.path.isfile(buttonFileName):
    try:
        print "Setting proper permissions on " + buttonFileName
        os.chmod(buttonFileName, 0744)
    except:
        pass

apikeysFileName = 'Clock/ApiKeys.py'
wuapi_re = re.compile('\\s*wuapi\\s*=')
dsapi_re = re.compile('\\s*dsapi\\s*=')
ccapi_re = re.compile('\\s*ccapi\\s*=')
owmapi_re = re.compile('\\s*owmapi\\s*=')

print "Checking " + apikeysFileName
if (os.path.isfile(apikeysFileName)):
    altered = False
    foundcc = False
    foundowm = False
    newfile = ''
    apikeys = open(apikeysFileName, "r")
    for aline in apikeys:
        if ccapi_re.match(aline):
            foundcc = True
        if owmapi_re.match(aline):
            foundwom = True
        if wuapi_re.match(aline):
            print "Removing wuapi key from " + apikeysFileName
            altered = True
        if dsapi_re.match(aline):
            print "Removing dsapi key from " + apikeysFileName
            altered = True
        else:
            newfile += aline
    apikeys.close()

    if not foundcc and not foundowm:
        print "This version of PiClock requires a ClimaCell api key."
        print "https://www.climacell.co/weather-api/"
        print "Enter your Climacell api key."
        print "key:",
        k = sys.stdin.readline()
        k = k.strip()
        if len(k) > 1:
            newfile += "ccapi = '" + k + "'"
            altered = True

    if altered:
        print "Writing Updated " + apikeysFileName
        apikeys = open(apikeysFileName, "w")
        apikeys.write(newfile)
        apikeys.close()
    else:
        print "No changes made to " + apikeysFileName

    try:
        from rpi_ws281x import *    # NOQA
    except:
        print "NeoAmbi.py now uses rpi-ws281x/rpi-ws281x-python"
        print "Please install it as follows:"
        print "sudo pip install rpi_ws281x"
