cd $HOME/PiClock
pkill -HUP -f PyQtPiClock.py
cd Clock
if [ "$DISPLAY" = "" ]
then
	export DISPLAY=:0
fi
# the main app
python -u PyQtPiClock.py $1 &
