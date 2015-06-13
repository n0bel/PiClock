# Install Instructions for PiClock (Clock Only)

This version of the instructions is for setting up just the clock
itself, ignoring all the other options.   It also assumes you have
some OS already setup.   So this is useful for setting up the 
clock on a desktop OS.

# Prerequisites

The minium requirements for a PiClock is pretty simple
* Python 2.7+ (but not 3)
* Python Qt4, known as PyQt4
* git (as an alternative to git, you can pull the zip file from git hub
(download button on the right side of the github project) then unzip it
onto your system )

Theses are available under Windows, Linux, and OSX OS's.

How to get these installed on your choice of system I'll leave
as an excersise for the reader.

### Get the PiClock software
```
git clone https://github.com/n0bel/PiClock.git
```
Alternatively, you can download a zip file of the github project.

https://github.com/n0bel/PiClock/archive/master.zip, then unzip it.


### Configure the PiClock api keys

The first is to set API keys for Weather Underground and Google Maps.  
These are both free, unless you have large volume.
The PiClock usage is well below the maximums  imposed by the free api keys.

Weather Underground api keys are created at this link: 
http://www.wunderground.com/weather/api/ Here too, it'll ask you for an
Application (maybe PiClock?) that you're using the api key with.

A _Google Maps api key is not required_, unless you pull a large volume of maps.
This *can* occur if you're continually pulling maps because you're restarting
the clock often durning development.   The maps are pulled once at the start.

If you want a key, this is how its done. Google Maps api keys are created at this link:
https://console.developers.google.com/flows/enableapi?apiid=maps_backend&keyType=CLIENT_SIDE
You'll require a google user and password.  After that it'll require
you create a "project" (maybe PiClock for a project name?)
It will also ask about Client Ids, which you can skip (just clock ok/create)

Now that you have your api keys...

```
cd PiClock
cd Clock
cp ApiKeys-example.py ApiKeys.py
[use your favorite editor] ApiKeys.py
```
Put your api keys in the file as indicated
```
#change this to your API keys
# Weather Underground API key
wuapi = 'YOUR WEATHER UNDERGROUND API KEY'
# Google Maps API key
googleapi = ''  #Empty string, the key is optional -- if you pull a small volume, you'll be ok
```

### Configure your PiClock
here's were you tell PiClock where your weather should come from, and the
radar map centers and markers. 

```
cd PiClock
cd Clock
cp Config-example.py Config.py  (copy on windows)
[use your favorite editor] Config.py
```

This file is a python script, subject to python rules and syntax.
The configuration is a set of variables, objects and arrays,
set up in python syntax.  The positioning of the {} and () and ','
are not arbitrary.  If you're not familiar with python, use extra
care not to disturb the format while changing the data.

The first thing is to change the Latitudes and Longitudes you see to yours.
They occur in several places. The first one in the file is where your weather
forecast comes from.   The others are where your radar images are centered
and where the markers appear on those images.  Markers are those little red
location pointers.

### Run it!

```
cd PiClock
python PyQtPiClock.py
```
After a few seconds, your screen should be covered by the PiClock  YAY!

There may be some output on the terminal screen as it executes.
If everything works, it can be ignored.  If for some reason the clock
doesn't work, or maps are missing, etc the output may give a reason
or reasons, which usually reference something to do with the config
file (Config.py)

### First Use

  * The space bar or right or left arrows will change the page.
  * F2 will start and stop the NOAA weather radio stream
  * F4 will close the clock
  

### Updating to newer/updated versions
Since we pulled the software from github originally, it can be updated
using git and github.
```
cd PiClock
git pull
python update.py
```
This will automatically update any part(s) of the software that has changed.
The update.py program will then convert any config files as needed.
