cd $HOME/PiClock
pkill -INT -f PyQtPiClock.py
cd Clock
if [ "$DISPLAY" = "" ]
then
	export DISPLAY=:0
fi
# the main app
# create a new log file name, max of 7 log files
echo "Rotating log files...."
rm PyQtPiClock.7.log >/dev/null 2>&1
mv PyQtPiClock.6.log PyQtPiClock.7.log >/dev/null 2>&1
mv PyQtPiClock.5.log PyQtPiClock.6.log >/dev/null 2>&1
mv PyQtPiClock.4.log PyQtPiClock.5.log >/dev/null 2>&1
mv PyQtPiClock.3.log PyQtPiClock.4.log >/dev/null 2>&1
mv PyQtPiClock.2.log PyQtPiClock.3.log >/dev/null 2>&1
mv PyQtPiClock.1.log PyQtPiClock.2.log >/dev/null 2>&1
# start the clock
echo "Starting PiClock...."
python -u PyQtPiClock.py $1 >PyQtPiClock.1.log 2>&1 &
