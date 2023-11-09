#!/bin/bash
# Update script for the PiClock

cd "$HOME"/PiClock || exit

# check if virtual environment exists
if [ -f "venv/bin/activate" ]; then
  echo "Activating virtual environment..."
  source venv/bin/activate
else
  echo "Creating virtual environment..."
  sudo apt update
  sudo apt install python3-full
  python3 -m venv --system-site-packages venv
  echo "Activating virtual environment..."
  source venv/bin/activate
fi

python3 update.py

echo "Deactivating virtual environment..."
deactivate
