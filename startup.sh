# Startup script for the PiClock
# Designed to be started from crontab as follows
#@reboot /home/pi/PiClock/startup.sh

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

# gpio button to keyboard input
sudo Button/gpio-keys 23:KEY_SPACE 24:KEY_F2

# for temperature sensor(s) on One Wire bus
cd Temperature
nohup python TempServer.py >/dev/null 2>&1 &
cd ..

# the main app
cd Clock
python PyQtPiClock.py Config-Chris
