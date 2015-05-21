# Install Instructions for PiClock

PiClock and this install guide are based on Raspian 2015-05-05 image released on https://www.raspberrypi.org/downloads/
It will work with many raspbian versions, but you may have to add more packages, etc.  That excersise is left for the reader.

What follows is a step by step guide.  If you start with a new clean raspbian image, it should just work.
I'm assuming that you already know how to hook up your Raspi, monitor, and keyboard/mouse.   If please 
do a web search regarding setting up the basic hardware for your Raspi.
 
### Download Raspbian and put it on an SD Card

The image and instructions for doing this are on the following page:
https://www.raspberrypi.org/downloads/  


### First boot and configure

When you first boot your Pi, you'll be presente with a configuration menu.  Generally on your second boot it will not
show up, and you'll need to do "sudo raspi-config".   Therefore I recommend doing these first step all at once.

1. Expand File system 
2. Change User Password -- this will set the password for the use pi, for ssh logins.
3. Enable Boot to Desktop/Scratch
   Pick the second option "Desktop Log in as user 'pi'....."
4. Internationalization
   Change Locale.
     Everything I've done is in English.  en_GB/UTF-8 will already be selected.
     If you're in the US, you'll probably want to also select en_US/UTF-8.   After that page is done, 
     you'll need to choose a default, again en_GB or en_US as you prefer.
   Change Timezone.
     You'll want this to be correct, or the clock will be wrong.
   Change Keyboard Layout
     Generally not needed, but good to check if you like the default
8. Advanced options
   Overscan
     Turn it off
   Hostname
     Maybe set this to PiClock?
   SSH
     I'd turn it on
   Audio
     Set as appropriate HDMI or Audio Jack outputs

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

You're free to change the pins, but of course the hardware guide will need to be adjusted to match.

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

Either connect to your wired network, or setup wifi and verify you have internet access from the Pi

```
ping github.com
```
(remember ctrl-c aborts programs, like breaking out of ping, which will go on forever)

### Get all the software that PiClock needs.

Become super user! (root)  <trumpets play in the background> (ok, maybe just in my head)
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
To get some things running, and ensure the final config is right, we'll do a reboot
```
reboot
```



#.................. more to come.. this is not complete
