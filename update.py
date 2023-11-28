import os
import re

print('\nUpdating Python Package Manager')
cmd = 'python3 -m pip install --upgrade pip'
print(cmd)
os.system(cmd)
print('\nRemoving old Python Modules')
cmd = 'python3 -m pip uninstall python-metar'
print(cmd)
os.system(cmd)
print('\nUpdating Python Modules')
cmd = 'python3 -m pip install -r requirements.txt'
print(cmd)
os.system(cmd)

buttonFileName = 'Button/gpio-keys'
print('\nChecking ' + buttonFileName)
if os.path.isfile(buttonFileName):
    print('Setting proper permissions on ' + buttonFileName)
    os.chmod(buttonFileName, 0o744)

apikeysFileName = 'Clock/ApiKeys.py'
wuapi_re = re.compile('\\s*wuapi\\s*=')
dsapi_re = re.compile('\\s*dsapi\\s*=')
ccapi_re = re.compile('\\s*ccapi\\s*=')
tmapi_re = re.compile('\\s*tmapi\\s*=')
owmapi_re = re.compile('\\s*owmapi\\s*=')

print('\nChecking ' + apikeysFileName)
if os.path.isfile(apikeysFileName):
    altered = False
    foundtm = False
    foundowm = False
    newfile = ''
    apikeys = open(apikeysFileName, 'r')
    for aline in apikeys:
        if tmapi_re.match(aline):
            foundtm = True
        if owmapi_re.match(aline):
            foundowm = True
        if wuapi_re.match(aline):
            print('Removing wuapi key from ' + apikeysFileName)
            altered = True
        if dsapi_re.match(aline):
            print('Removing dsapi key from ' + apikeysFileName)
            altered = True
        if ccapi_re.match(aline):
            print('Removing ccapi key from ' + apikeysFileName)
            altered = True
        else:
            newfile += aline
    apikeys.close()

    if not foundtm and not foundowm:
        print('\nThis version of PiClock requires a new weather API key.')
        while 1:
            print('Please select your weather provider:')
            print('  <1> OpenWeatherMap.org (https://openweathermap.org/price)')
            print('  <2> Tomorrow.io (https://www.tomorrow.io/weather-api/)')
            print('Selection (1 or 2)')
            choice = int(input('? '))
            if 1 <= choice <= 2:
                break
        if choice == 1:
            print('Enter your OpenWeatherMap.org API key.')
            print('key: '),
            k = input('key: ')
            k = k.strip()
            if len(k) > 1:
                newfile += 'owmapi = \'' + k + '\''
                altered = True
        else:
            print('Enter your Tomorrow.io API key.')
            k = input('key: ')
            k = k.strip()
            if len(k) > 1:
                newfile += 'tmapi = \'' + k + '\''
                altered = True

    if altered:
        print('\nWriting updated ' + apikeysFileName)
        apikeys = open(apikeysFileName, 'w')
        apikeys.write(newfile)
        apikeys.close()
    else:
        print('No changes made to ' + apikeysFileName)

    try:
        from rpi_ws281x import *  # NOQA
    except ModuleNotFoundError:
        print('\nERROR: rpi_ws281x not found')
        print('NeoAmbi.py now uses rpi-ws281x/rpi-ws281x-python')
        print('Please install it as follows:')
        print('python3 -m pip install rpi_ws281x')
