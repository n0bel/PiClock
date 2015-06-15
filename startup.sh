# Startup script for the PiClock
# Designed to be started from crontab as follows
#@reboot sh /home/pi/PiClock/startup.sh

#
cd /home/pi/PiClock

# wait for Xwindows and the desktop to start up
sleep 45

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
cd Leds
sudo python NeoAmbi.py &
cd ..

# gpio button to keyboard input
sudo Button/gpio-keys 23:KEY_SPACE 24:KEY_F2 25:KEY_UP &

# for temperature sensor(s) on One Wire bus
cd Temperature
python TempServer.py &
cd ..

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
python PyQtPiClock.py >$lf 2>&1
