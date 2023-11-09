# Install Instructions for PiClock
## For Raspberry Pi OS

PiClock and this install guide are based on Raspberry Pi OS downloaded from
https://www.raspberrypi.com/software/. I suggest using
"Raspberry Pi OS with desktop".  It will work with many Raspberry Pi OS versions,
but you may have to add more packages, etc.  That exercise is left for the reader.

What follows is a step-by-step guide.  If you start with a new clean Raspberry Pi OS
image, it should just work. I'm assuming that you already know how to hook
up your Raspi, monitor, and keyboard/mouse.   If not, please do a web search
regarding setting up the basic hardware for your Raspi.

### Download Raspberry Pi OS and put it on an SD Card

The instructions for doing this are on the following page:
https://www.raspberrypi.com/documentation/computers/getting-started.html

### First boot and configure
A keyboard and mouse are really handy at this point.
When you first boot your Pi, you'll be presented with the desktop.
Following this there will be several prompts to set things up, follow
those prompts and set things as they make sense for you.  Of course
setting the proper timezone for a clock is key.

Eventually the Pi will reboot, and you'll be back to the desktop.
You need to configure a few more things.

Navigate to Menu->Preferences->Raspberry Pi Configuration.
Just change the Items below.
 - System Tab
  - Hostname: (Maybe set this to PiClock?)
  - Boot: To Desktop
  - Auto Login: Checked
  - Overscan: (Initially leave as default, but if your monitor has extra
    black area on the border, or bleeds off the edge, then change this)
 - Interfaces
  - 1-Wire Enable (for the inside temperature, DS18B20 if you're using it)
  - SSH is handy (if you'd like to connect to your clock from another computer)
  - VNC can be handy  (same reason as ssh)


Click ok, and allow it to reboot.

### Get connected to the internet

Log into your Pi, (either on the screen or via ssh). 

Verify you have internet access from the Pi.

```
ping github.com
```
(remember ctrl-c aborts programs, like breaking out of ping, which will
go on forever)

### Get all the software that PiClock needs
Update the package repository and get the full Python3 and Qt5 for Python
```
sudo apt update
sudo apt install python3-full python3-pyqt5
```
You may need to confirm some things, like:
After this operation, 59.5 MB of additional disk space will be used.
Do you want to continue [Y/n]? 
Go ahead, say yes.

### Get the PiClock software
Log into your Pi, (either on the screen or via ssh) (NOT as root).
You'll be in the home directory of the user pi (/home/pi) by default,
and this is where you want to be.  Note that the following command while
itself not being case-sensitive, further operation of PiClock may be
affected if the upper and lower case of the command is not followed.
```
git clone https://github.com/SerBrynden/PiClock.git
```

Once that is done, you'll have a new directory called PiClock.

### Create virtual environment
Create a Python virtual environment in the PiClock directory for 
installing the required Python packages and running PiClock.
```
cd PiClock
python3 -m venv --system-site-packages venv
```
Activate the virtual environment in the PiClock directory 
before you install any Python packages.
```
source venv/bin/activate
```
You will know you are working in the virtual environment when the 
command prompt begins with (venv). 
It will look something like this:
```
(venv) pi@piclock:~/PiClock $
```

### Required software packages
Once inside the virtual environment, install required Python packages
```
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```
then get unclutter (disables the mouse pointer when there's no activity)
```
sudo apt install unclutter
```
### Optional software packages
#### Optional - NeoPixel LED Driver
Get optional ws281x driver for Python if using NeoPixel LEDs
```
python3 -m pip install rpi_ws281x
```
Some versions of Raspberry Pi OS need python3-dev to be installed as well, before
rpi-ws281x can be installed.  If the previous command fails reporting
a missing include file, then do this:
```
sudo apt install python3-dev
python3 -m pip install rpi_ws281x
```

#### Optional - DS18B20 Temperature Driver
Get optional DS18B20 Temperature driver for Python if using indoor temperature sensors
```
git clone https://github.com/timofurrer/w1thermsensor.git && cd w1thermsensor
sudo python3 setup.py install
```

#### Optional - Lirc IR Remote Driver
Get optional Lirc driver if using IR remote
```
sudo apt install lirc
```
use nano to edit lirc options file
```
sudo nano /etc/lirc/lirc_options.conf
```
Be sure the uinput line appears as follows
```
uinput         = True
```
Be sure the driver line appears as follows
```
driver          = default
```

#### Optional - mpg123 Audio Streaming
Get optional mpg123 to play NOAA weather radio streams
```
sudo apt install mpg123
```

### Optional - Editing config.txt

(Only required if you will be using IR Remote control or DS18B20 temperature
 sensors)

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

### Exit virtual environment
The leave the virtual environment, use the following command
```
deactivate
```

### Reboot
To get some things running, and ensure the final config is right, do
a reboot
```
sudo reboot
```

Log into your Pi, (either on the screen or via ssh) (NOT as root).
You'll be in the home directory of the user pi (/home/pi) by default.

### Optional - Set up GPIO keys

A few commands are needed if you intend to use gpio buttons
and the gpio-keys driver to compile it for the latest Raspberry Pi OS:
```
cd PiClock/Button
make gpio-keys
cd ../..
```

### Optional - Set up Lirc IR Remote

If you're using the recommended IR Key Fob,
https://www.google.com/search?q=Mini+Universal+Infrared+IR+TV+Set+Remote+Control+Keychain
you can copy the lircd.conf file included in the distribution as follows:
```
sudo cp IR/lircd.conf /etc/lirc/lircd.conf.d/
```
If you're using something else, you'll need to use irrecord, or load a remote file
as found on http://lirc.org/

The software expects 7 keys.   KEY_F1, KEY_F2, KEY_F3, KEY_UP, KEY_DOWN, KEY_RIGHT
and KEY_LEFT.   Lirc takes these keys and injects them into linix as if they
were typed from a keyboard.   PyQtPiClock.py then simply looks for normal keyboard
events.   Therefore, of course, if you have a USB keyboard attached, those keys
work too.  On the key fob remote, F1 is power, F2 is mute and F3 is AV/TV.

You should (must) verify your IR codes.   I've included a program called IRCodes.pl
which will verify that your lircd.conf is set up correctly.
If you've rebooted after installing lircd.conf, you'll have to stop lirc first:
```
sudo service lirc stop
```
Then use the IRCodes.pl program as follows:
```
perl IR/IRCodes.pl
```
Yes, I reverted to perl... I may redo it in Python one day.

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


### Configure the PiClock API keys

You need to set API keys for one weather service and one map service.
These are free unless you have large volume.
The PiClock usage is well below the maximums imposed by the no cost API keys.

#### Weather API Key

You have your choice of OpenWeather or Tomorrow from which to get your 
current weather and forcast data.
You only need one or the other (owmapi or tmapi)

#### OpenWeather API key

An OpenWeather API key is required to use OpenWeather data.

OpenWeather API keys are created by signing up at this link:
https://openweathermap.org/price

Select either the One Call by Call API 3.0 subscription plan, or scroll down for the 
Professional Collections current weather and forecasts free plan.

The OpenWeather One Call by Call API 3.0 key requires a credit card which won't be charged 
unless usage is high. If you subscribe to the One Call API 3.0 plan, the default call limit is set 
to 2,000 API calls per day, however only the first 1,000 calls are free, which 
you should not exceed under typical PiClock operation.
After the daily limit is reached, the overage charge is $0.15 per 100 calls.
To be safe, it is recommended you change the daily limit by going to the 
"Billing plans" tab in your OpenWeather Personal account, and change the standard 
"Calls per day (no more than)" setting to 1,000 calls.

#### Tomorrow API key

A Tomorrow API key is required to use Tomorrow weather data.

Tomorrow API keys are created by signing up at this link:
https://www.tomorrow.io/weather-api/

#### Map API Key

You have your choice of Mapbox or Google Maps from which to get your underlying maps.
You only need one or the other (mbapi or googleapi)

#### Google Maps API key

A Google Maps API key is required to use Google Maps.
(Requires credit card which won't be charged unless usage is high.)

An intro to Google static maps API keys, and a link to creating your account and API keys:
https://developers.google.com/maps/documentation/maps-static/intro
You'll require a Google user and password.  It'll also require a credit card.
The credit card should not be charged, because my reading of
https://cloud.google.com/maps-platform/pricing/sheet/ the $200.00 credit will
apply, and your charges incurred will be for 31 map pulls per month will be
$0.62 , if you reboot daily.
You'll be required to create a "project" (maybe PiClock for a project name?)
You need to then activate the key.

_Protect your API keys._  You'd be surprised how many pastebin's are out
there with valid API keys, because of people not being careful.   _If you post
your keys somewhere, your usage will skyrocket, and your bill as well._  Google
has the ability to add referer, device and IP requirements on your API key.  It
can also allow you to limit an API key to specific applications only (static-maps)
in this case. Also, you might consider disabling all the other APIs on your
project dashboard. Under the Billing section of things you can set up budgets
and alerts (set to like $1.00).

#### Mapbox API key

A Mapbox API key (access token) is required to use Mapbox.

Mapbox access tokens are created by signing up at this link:
https://www.mapbox.com/signup/

Now that you have your API keys...

```
cd PiClock/Clock
cp ApiKeys-example.py ApiKeys.py
nano ApiKeys.py
```
Put your API keys in the file as indicated
```
# Change this to your API keys

# Map API keys -- only need 1 of the following
# Google Maps API key (if usemapbox is not set in Config)
googleapi = 'YOUR GOOGLE MAPS API KEY'
# Mapbox API key (access_token) [if usemapbox is set in Config]
mbapi = 'YOUR MAPBOX ACCESS TOKEN'

# Weather API key -- only need 1 of the following
# If you want to use OpenWeatherMap.org, uncomment and add API key
owmapi = 'YOUR OPENWEATHERMAP API KEY'
# If you want to use Tomorrow.io, uncomment and add API key
# tmapi = 'YOUR TOMORROW API KEY'
```

### Configure your PiClock
Here's where you tell PiClock where your weather should come from, and the
radar map centers and markers.

```
cd PiClock/Clock
cp Config-Example.py Config.py
nano Config.py
```

This file is a python script, subject to python rules and syntax.
The configuration is a set of variables, objects and arrays,
set up in python syntax.  The positioning of the {} and () and ','
are not arbitrary.  If you're not familiar with python, use extra
care not to disturb the format while changing the data.

The first thing is to change the primary_coordinates to yours.  That is really
all that is mandatory.  Further customization of the radar maps can be done in
the Radar section.  There you can customize where your radar images are centered
and where the markers appear on those images.  Markers are those little red
location pointers.  Radar1 and 2 show on the first page, and 3 and 4 show on the
second page of the display (here's a post of about that:
https://www.facebook.com/permalink.php?story_fbid=1371576642857593&id=946361588712436&substory_index=0)

The second thing to change is your NOAA weather radio stream url.  You can
find it here: http://noaaweatherradio.org/  They don't put the .mp3 urls
where they are easily accessible, so you need to use your browser to "View Page Source"
in order to find the proper .mp3 url.

At this point, I'd not recommend many other changes until you have tested
and gotten it running.

### Run it!
You'll need to be on the desktop, in a terminal program.

```
cd PiClock
bash startup.sh -n -s
```
Your screen should be covered by the PiClock  YAY!

There will be some output on the terminal screen as startup.sh executes.
If everything works, it can be ignored.  If for some reason the clock
doesn't work, or maps are missing, etc. the output may give a reason
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
then
```
nano Temperature/TempNames.py
```
Give each number a name, like is shown in the examples in that file

### Setting the clock to auto start
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
This puts the PiClock icon on your desktop.  It also runs it when
the desktop starts.

## Autostart Method 2
To have it auto start on boot you need to do one more thing, edit the
crontab file as follows: (it will automatically start nano)  (NOT as root)
```
crontab -e
```
and add the following line:
```
@reboot bash /home/pi/PiClock/startup.sh
```
save the file
and reboot to test
```
sudo reboot
```

## Some notes about startup.sh
startup.sh has a few options:
* -n or --no-delay&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;Don't delay on starting the clock right away (default is 45 seconds delay)
* -d X or --delay X&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;Delay X seconds before starting the clock
* -m X or --message-delay X&emsp;&emsp;Delay X seconds while displaying a message on the desktop

Startup also looks at the various optional PiClock items (Buttons, Temperature, NeoPixel, etc.)
and only starts those things that are configured to run.   It also checks if they are already
running, and refrains from starting them again if they are.

### Switching skins at certain times of the day
This is optional, but if its just too bright at night, a switcher script will kill and restart
PyQtPiClock with an alternate config.

First you need to set up an alternate config.   Config.py is the normal name, so perhaps Config-Night.py
might be appropriate.  For a dimmer display use Config-Example-Bedside.py as a guide.

First you must make switcher.sh executable (git removes the x flags)
```
cd PiClock
chmod +x switcher.sh
```
Now tell your friend cron to run the switcher script (switcher.sh) on day/night cycles.
Run the cron editor: (should *not* be root)
```
crontab -e
```
Add lines similar to this:
```
0 8 * * * bash /home/pi/PiClock/switcher.sh Config
0 21 * * * bash /home/pi/PiClock/switcher.sh Config-Night
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
Since you pulled the software from GitHub originally, it can be updated
using git and GitHub.
```
cd PiClock
git pull
bash update.sh
```
This will automatically update any part(s) of the software that has changed.
The update.sh script will then convert any config files as needed.

You'll want to reboot after the update.

Note: If you get errors because you've made changes to the base code you might need
```
git diff
```
To see your changes, so you can back them up

Then this will update to the current version
```
git reset --hard
```
(This won't bother your Config.py nor ApiKeys.py because they are not tracked in git.)

Also, if you're using gpio-keys, you may need to remake it:
```
cd PiClock/Button
rm gpio-keys
make gpio-keys
```
