cd /home/pi/PiClock
pkill -HUP -f PyQtPiClock.py
cd Clock
export DISPLAY=:0.0
# create a new log file name, max of 7 log files
lc=`expr $(cat log.count 2>/dev/null) + 1`
if [ "$lc" -gt "7" ]
then
  lc=1
fi
echo $lc >log.count
lf="PyQtPiClock.$lc.log"
# start the clock
python -u PyQtPiClock.py $1 >$lf 2>&1
