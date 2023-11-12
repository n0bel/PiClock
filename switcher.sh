#!/bin/bash
cd "$HOME"/PiClock || exit
pkill -INT -f PyQtPiClock.py
# virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
# the main app
cd Clock || exit
if [ "$DISPLAY" = "" ]; then
  export DISPLAY=:0
fi
# create a new log file name, max of 7 log files
echo "Rotating log files..."
rm PyQtPiClock.7.log >/dev/null 2>&1
mv PyQtPiClock.6.log PyQtPiClock.7.log >/dev/null 2>&1
mv PyQtPiClock.5.log PyQtPiClock.6.log >/dev/null 2>&1
mv PyQtPiClock.4.log PyQtPiClock.5.log >/dev/null 2>&1
mv PyQtPiClock.3.log PyQtPiClock.4.log >/dev/null 2>&1
mv PyQtPiClock.2.log PyQtPiClock.3.log >/dev/null 2>&1
mv PyQtPiClock.1.log PyQtPiClock.2.log >/dev/null 2>&1
echo "Starting PiClock... logging to Clock/PyQtPiClock.1.log"
# start PiClock and add timestamp to log output
python3 -u PyQtPiClock.py "$1" 2>&1 | (while read -r line; do echo "$(date +'[%F %T.%6N]') $line"; done) >PyQtPiClock.1.log
