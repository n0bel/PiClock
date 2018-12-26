import sys
import os.path
import re

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

print "Checking " + apikeysFileName
if (os.path.isfile(apikeysFileName)):
    altered = False
    foundds = False
    newfile = ''
    apikeys = open(apikeysFileName, "r")
    for aline in apikeys:
        if dsapi_re.match(aline):
            foundds = True
        if wuapi_re.match(aline):
            print "Removing wuapi key from " + apikeysFileName
            altered = True
        else:
            newfile += aline
    apikeys.close()

    if not foundds:
        print "This version of PiClock requires a DarkSky api key."
        print "https://darksky.net/dev"
        print "Enter your DarkSky api key."
        print "key:",
        k = sys.stdin.readline()
        k = k.strip()
        if len(k) > 1:
            newfile += "dsapi = '" + k + "'"
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
