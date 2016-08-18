# Startup script for the PiClock
# Designed to be started from crontab as follows
#@reboot sh /home/pi/PiClock/startup.sh

#
cd $HOME/PiClock

# wait for Xwindows and the desktop to start up
if [ "$1" != "-n" -a "$1" != "--no-sleep" ]
then
	sleep 45
fi

# stop screen blanking
export DISPLAY=:0.0
xset s off
xset -dpms
xset s noblank

# get rid of mouse cursor
unclutter &

# push sound level to maximum
amixer cset numid=1 -- 400

# NeoPixel AmbiLights
python -c "import NeoPixel"
if [ $? -eq 0 ]
	then
	cd Leds
	sudo python NeoAmbi.py &
	cd ..
fi

# gpio button to keyboard input
if [ -x Button/gpio-keys ]
	then
	sudo Button/gpio-keys 23:KEY_SPACE 24:KEY_F2 25:KEY_UP &
fi

# for temperature sensor(s) on One Wire bus
python -c "import w1thermsensor"
if [ $? -eq 0 ]
	then
	cd Temperature
	python TempServer.py &
	cd ..
fi

# the main app
cd Clock
# create a new log file name, max of 7 log files
lc=`expr $(cat log.count 2>/dev/null) + 1`
if [ "$lc" -gt "7" ]
then
  lc=1
fi
echo $lc >log.count
lf="PyQtPiClock.$lc.log"
# start the clock
python -u PyQtPiClock.py >$lf 2>&1
