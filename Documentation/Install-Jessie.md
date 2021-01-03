# Install Instructions for PiClock
## For Raspbian Jessie

PiClock and this install guide are based on Raspian Jessie
last released on https://downloads.raspberrypi.org/raspbian/images/raspbian-2017-07-05/
It will work with many raspbian versions, but you may have to add more packages,
etc.  That exercise is left for the reader.

What follows is a step by step guide.  If you start with a new clean raspbian
image, it should just work. I'm assuming that you already know how to hook
up your Raspi, monitor, and keyboard/mouse.   If not, please do a web search
regarding setting up the basic hardware for your Raspi.

### Download Raspbian Jessie and put it on an SD Card

The image and instructions for doing this are on the following page:
https://www.raspberrypi.org/downloads/

### First boot and configure
A keyboard and mouse are really handy at this point.
When you first boot your Pi, you'll be presented with the desktop.
Navigate to Menu->Preferences->Raspberry Pi Configuration.
Just change the Items below.
 - General Tab
  - Change User Password -- this will set the password for the use pi,
     for ssh logins.
  - Hostname: (Maybe set this to PiClock?)
  - Boot: To Desktop
  - Auto Login: Checked
  - Underscan: (Initally leave as default, but if your monitor has extra black area on the border, or bleeds off the edge, then change this)
 - Interfaces
  - 1-Wire Enable (for the inside temperature, DS18B20 if you're using it)
 - Internationalization Tab
   - Set Locale.
    - Set Language  -- if you set language and country here, the date will automaticly be in your language
    				-- other settings in Config.py (described later) control the language of the weather data
    - Set Country
    - Character Set: UTF-8
  - Set Timezone.
    -  You'll want this to be correct, or the clock will be wrong.
  - Set Keyboard
    -  Generally not needed, but good to check if you like the default
  - Set WiFi Country (may not always show up)

Finish and let it reboot.

I've found that sometimes on reboot, Jessie doesn't go back to desktop mode.
If this is the case,
```
sudo raspi-config
```
and change the boot option to Desktop/Auto-login

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
The default config has lirc-rpi commented out (# in front), don't forget to remove the #
Also add the pin arguments just as shown above, if they are not already there.

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

then get ws281x driver for python (optional for the NeoPixel LED Driver)
```
pip install rpi_ws281x
```
Someversions of Raspbian need python-dev to be installed as well, before
rpi-ws281x can be installed.  If the prevous command fails reporting
a missing include file, then do this:
```
apt-get install python-dev
```
Then try the pip command again.

then install more needed python libraries
```
pip install python-dateutil --upgrade
pip install tzlocal --upgrade
pip install python-metar --upgrade
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

Be sure the DEVICE line appears as follows
```
DEVICE="/dev/lirc0"
```

Be sure the MODULES line appears as follows
```
MODULES="lirc_rpi"
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
A few commands are needed if you intend to use gpio buttons
and the gpio-keys driver to compile it for the latest Raspbian:
```
cd PiClock/Button
make gpio-keys
cd ../..
```

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

The first is to set API keys for DarkSky and Google Maps.
These are both free, unless you have large volume.
The PiClock usage is well below the maximums imposed by the no cost api keys.

#### DarkSky api keys

DarkSky api keys are created at this link:
https://darksky.net/dev

#### Google Maps API key

A Google Maps api key is _required_.  (Requires credit card which won't be
charged unless usage is great.)

An intro to Google static maps api keys, and a link to creating your account and ApiKeys:
https://developers.google.com/maps/documentation/maps-static/intro
You'll require a google user and password.  It'll also require a credit card.
The credit card should not be charged, because my reading of https://cloud.google.com/maps-platform/pricing/sheet/ the $200.00 credit will
apply, and your charges incurred will be for 31 map pulls per month will be
$0.62 , if you reboot daily.
You'll be required to create a "project" (maybe PiClock for a project name?)
You need to then activate the key.

_Protect your API keys._  You'd be surprised how many pastebin's are out
there with valid API keys, because of people not being careful.   If you post
your keys somewhere, your usage will skyrocket, and your bill as well.  Google
has the ability to add referer, device and ip requirements on your api key.  It
can also allow you to limit an api key to specific applications only (static-maps)
in this case.   Also you might consider disabling all the other APIs on your
project dashboard.   Under the Billing section of things you can set up budgets
and alerts.  (Set to like $1.00)


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
# DarkSky API key
dsapi = 'YOUR DARKSKY API KEY'
# Google Maps API key
googleapi = 'YOUR GOOGLE API KEY'
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

The first thing is to change the primary_coordinates to yours.  That is really
all that is manditory.  Further customization of the radar maps can be done in
the Radar section.  There you can customize where your radar images are centered
and where the markers appear on those images.  Markers are those little red
location pointers.  Radar1 and 2 show on the first page, and 3 and 4 show on the
second page of the display (here's a post of about that:
https://www.facebook.com/permalink.php?story_fbid=1371576642857593&id=946361588712436&substory_index=0 )

The second thing to change is your NOAA weather radio stream url.  You can
find it here: http://noaaweatherradio.org/  They don't put the .mp3 urls
where they are easily accessable, so you need to use your browser to "View Page Source"
in order to find the proper .mp3 url.

At this point, I'd not recommend many other changes until you have tested
and gotten it running.

### Run it!
You'll need to be on the desktop, in a terminal program.

```
cd PiClock
sh startup.sh -n -s
```
Your screen should be covered by the PiClock  YAY!

There will be some output on the terminal screen as startup.sh executes.
If everything works, it can be ignored.  If for some reason the clock
doesn't work, or maps are missing, etc the output may give a reason
or reasons, which usually reference something to do with the config
file (Config.py)

### Logs
The -s option causes no log files to be created, but
instead logs to your terminal screen.  If -s is omitted, logs are
created in PiClock/Clock as PyQtPiClock.[1-7].log, which can also help
you find issues.  -s is normally omitted when started from the desktop icon
or from crontab.  Logs are then created for debugging auto starts.

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

Use only one autostart method.
## Autostart Method 1
(NOT as root)
```
cd PiClock
chmod +x PiClock.desktop
ln PiClock.desktop ~/Desktop
mkdir ~/.config/autostart
ln PiClock.desktop ~/.config/autostart
```
This puts the a PiClock icon on your desktop.  It also runs it when
the desktop starts.

## Autostart Method 2
To have it auto start on boot we need to do one more thing, edit the
crontab file as follows: (it will automatically start nano)  (NOT as root)
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

## Some notes about startup.sh
startup.sh has a few options:
* -n or --no-delay			Don't delay on starting the clock right away (default is 45 seconds delay)
* -d X or --delay X			Delay X seconds before starting the clock
* -m X or --message-delay X 	Delay X seconds while displaying a message on the desktop

Startup also looks at the various optional PiClock items (Buttons, Temperature, NeoPixel, etc)
and only starts those things that are configured to run.   It also checks if they are already
running, and refrains from starting them again if they are.

### Switching skins at certain times of the day
This is optional, but if its just too bright at night, a switcher script will kill and restart
PyQtPiClock with an alternate config.

First you need to set up an alternate config.   Config.py is the normal name, so perhaps Config-Night.py
might be appropriate.  For a dimmer display use Config-Example-Bedside.py as a guide.

Now we'll tell our friend cron to run the switcher script (switcher.sh) on day/night cycles.
Run the cron editor: (should *not* be roor)
```
crontab -e
```
Add lines similar to this:
```
0 8 * * * sh /home/pi/PiClock/switcher.sh Config
0 21 * * * sh /home/pi/PiClock/switcher.sh Config-Night
```
The 8 there means 8am, to switch to the normal config, and the 21 means switch to Config-Night at 9pm.
More info on crontab can be found here: https://en.wikipedia.org/wiki/Cron

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

Note: If you get errors because you've made changes to the base code you might need
```
git reset --hard
```
Backup your changes first!
(This won't bother your Config.py nor ApiKeys.py because they are not tracked in git.

Also, if you're using gpio-keys, you may need to remake it:
```
cd PiClock/Buttons
rm gpio-keys
make gpio-keys
```
