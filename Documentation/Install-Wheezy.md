# Install Instructions for PiClock
## For Raspbian Wheezy

PiClock and this install guide are based on Raspian Wheezy 2015-05-05 image
released on https://www.raspberrypi.org/downloads/ It will work with many
raspbian versions, but you may have to add more packages, etc.  That exercise
is left for the reader.

What follows is a step by step guide.  If you start with a new clean raspbian
image, it should just work. I'm assuming that you already know how to hook
up your Raspi, monitor, and keyboard/mouse.   If not, please do a web search
regarding setting up the basic hardware for your Raspi.
 
### Download Raspbian Wheezy and put it on an SD Card

The image and instructions for doing this are on the following page:
https://www.raspberrypi.org/downloads/  HOWEVER: Jessie is rolled
into the latest download for Raspbian. and Wheezy has been removed
from the download page. Some hardware functions (temperature, buttons, ir)
won't work if you use Wheezy. (Yes, I need to get to updating some of
the PiClock software to get this to work).  The last version of 
Wheezy is archived here: 
https://downloads.raspberrypi.org/raspbian/images/raspbian-2015-05-07/2015-05-05-raspbian-wheezy.zip


### First boot and configure

When you first boot your Pi, you'll be presented with a configuration menu.
Generally on your second boot it will not show up, and you'll need to do
"sudo raspi-config".   Therefore I recommend doing these first steps
all at once.

  - Expand File system -- do it
  - Change User Password -- this will set the password for the use pi,
     for ssh logins.
  - Enable Boot to Desktop/Scratch
    * Pick the second option "Desktop Log in as user 'pi'....."
  - Internationalization
    * Change Locale.
      - Everything I've done is in English.  en_GB/UTF-8 will already 
      be selected. If you're in the US, you'll probably want to also
      select en_US/UTF-8. After that page is done, you'll need to choose
      a default, again en_GB or en_US as you prefer.
  - Change Timezone.
    *  You'll want this to be correct, or the clock will be wrong.
  - Change Keyboard Layout
    *  Generally not needed, but good to check if you like the default
  - Advanced options
    * Overscan
      - Turn it off
    * Hostname
      - Maybe set this to PiClock?
    * SSH
      - I'd turn it on
    * Audio
      - Set as appropriate HDMI or Audio Jack outputs, to your monitor or speaker setup.

Finish and let it reboot.

### editing config.txt

Log into your Pi, (either on the screen or via ssh)

use nano to edit the boot config file
```
sudo nano /boot/config.txt
``` 
Be sure the lines
``` 
dtoverlay=lirc-rpi,gpio_in_pin=3,gpio_out_pin=2
dtoverlay=w1-gpio,gpiopin=4
```
are in there somewhere, and occur only once.

You're free to change the pins, but of course the hardware guide will need to
be adjusted to match.

use nano to edit the modules file
```
sudo nano /etc/modules
```
Be sure the lines
```
lirc_rpi gpio_in_pin=3 gpio_out_pin=2
w1-gpio
```
are in there somewhere, and only occur once.

reboot
```
sudo reboot
```

### Get connected to the internet

Either connect to your wired network, or setup wifi and verify you have
internet access from the Pi

```
ping github.com
```
(remember ctrl-c aborts programs, like breaking out of ping, which will
go on forever)

### Get all the software that PiClock needs.

Become super user! (root)  (trumpets play in the background) (ok, maybe
just in my head)
```
sudo su -
```
update the repository
```
apt-get update
```
then get qt4 for python
```
apt-get install python-qt4
```
you may need to confirm some things, like:
After this operation, 44.4 MB of additional disk space will be used.
Do you want to continue [Y/n]? y
Go ahead, say yes

then get libboost for python (optional for the NeoPixel LED Driver)
```
apt-get install libboost-python1.49.0
```

then get unclutter (disables the mouse pointer when there's no activity)
```
apt-get install unclutter
```

### Get the DS18B20 Temperature driver for Python (optional)

(you must still be root [super user]) 
```
git clone https://github.com/timofurrer/w1thermsensor.git && cd w1thermsensor
python setup.py install
```

### Get Lirc driver for IR remote (optional)

(you must still be root [super user]) 
```
apt-get install lirc
```

use nano to edit lirc hardware file
```
sudo nano /etc/lirc/hardware.conf
```
Be sure the LIRCD_ARGS line appears as follows
```
LIRCD_ARGS="--uinput"
```

Be sure the DRIVER line appears as follows
```
DRIVER="default"
```

### Get mpg123 (optional to play NOAA weather radio streams)

(you must still be root [super user]) 
```
apt-get install mpg123
```

### reboot
To get some things running, and ensure the final config is right, we'll do
a reboot
```
reboot
```

### Get the PiClock software
Log into your Pi, (either on the screen or via ssh) (NOT as root)
You'll be in the home directory of the user pi (/home/pi) by default,
and this is where we want to be.
```
git clone https://github.com/n0bel/PiClock.git
```
Once that is done, you'll have a new directory called PiClock
One little command is needed if you intend to use gpio buttons
and the gpio-keys driver:
```
chmod +x PiClock/Button/gpio-keys
```
(git hub does not allow me to set attributes on files, so we
must do it manually)

### Set up Lirc (IR Remote)
If you're using the recommended IR Key Fob, 
https://www.google.com/search?q=Mini+Universal+Infrared+IR+TV+Set+Remote+Control+Keychain
you can copy the lircd.conf file included in the distribution as follows:
```
sudo cp IR/lircd.conf /etc/lirc/
```
If you're using something else, you'll need to use irrecord, or load a remote file
as found on http://lirc.org/

The software expects 7 keys.   KEY_F1, KEY_F2, KEY_F3, KEY_UP, KEY_DOWN, KEY_RIGHT
and KEY_LEFT.   Lirc takes these keys and injects them into linix as if they
were typed from a keyboard.   PyQPiClock.py then simply looks for normal keyboard
events.   Therefore of course, if you have a usb keyboard attached, those keys
work too.  On the key fob remote, F1 is power, F2 is mute and F3 is AV/TV. 

You should (must) verify your IR codes.   I've included a program called IRCodes.pl
which will verify that your lircd.conf is setup correctly.
If you've rebooted after installing lircd.conf, you'll have to stop lirc first:
```
sudo service lirc stop
```
Then use the IRCodes.pl program as follows:
```
perl IR/IRCodes.pl
```
Yes, I reverted to perl.. I may redo it in Python one day.

If you're using the recommended key fob remote, they come randomly programmed from
the supplier.   To program them you press and hold the mute button (the middle one)
while watching the screen scroll through codes.
When the screen shows 
```
************ KEY_F2
```
STOP! then try the other keys, be sure they all report KEY_UP, KEY_DOWN correctly.
If not press and hold the mute button again, waiting for the asterisks and KEY_F2,
then STOP again, try the other keys.   Repeat the process until you have all the 
keys working.

Ctrl-C to abort perl.

then reboot
```
sudo reboot
```


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
nano ApiKeys.py
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
cp Config-Example.py Config.py
nano Config.py
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

The second thing to change is your NOAA weather radio stream url.  You can
find it here: http://www.wunderground.com/wxradio/

At this point, I'd not recommend many other changes until you have tested
and gotten it running.

### Run it!

```
cd PiClock
sh startup.sh
```
After about 45 seconds, your screen should be covered by the PiClock  YAY!

There may be some output on the terminal screen as startup.sh executes.
If everything works, it can be ignored.  If for some reason the clock
doesn't work, or maps are missing, etc the output may give a reason
or reasons, which usually reference something to do with the config
file (Config.py)

### First Use

  * The space bar or right or left arrows will change the page.
  * F2 will start and stop the NOAA weather radio stream
  * F4 will close the clock
  
If you're using the temperature feature AND you have multiple temperature sensors,
you'll see the clock display: 000000283872:74.6 00000023489:65.4 or something similar.
Note the numbers exactly.   Use F4 to stop the clock,
then..
```
nano Temperature/TempNames.py
```
Give each number a name, like is shown in the examples in that file

### setting the clock to auto start
At this point the clock will only start when you manually start it, as
described in the Run It section.

To have it auto start on boot we need to do one more thing, edit the
crontab file as follows: (it will automatically start nano)
```
crontab -e
```
and add the following line:
```
@reboot sh /home/pi/PiClock/startup.sh
```
save the file
and reboot to test
```
sudo reboot
```

### Setting the Pi to auto reboot every day
This is optional but some may want their PiClock to reboot every day.  I do this with mine,
but it is probably not needed.
```
sudo crontab -e
```
add the following line
```
22 3 * * * /sbin/reboot
```
save the file

This sets the reboot to occur at 3:22am every day.   Adjust as needed.


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

You'll want to reboot after the update.

