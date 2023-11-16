#!/bin/bash
# Update script for the PiClock

cd "$HOME"/PiClock || exit

# check if virtual environment exists
if [ -f "venv/bin/activate" ]; then
  echo "Activating virtual environment..."
  source venv/bin/activate || exit
else
  echo "Virtual environment not found"
  echo "Updating Python3..."
  sudo apt update
  sudo apt install python3-full
  echo "Creating virtual environment..."
  python3 -m venv --system-site-packages venv
  echo "Activating virtual environment..."
  source venv/bin/activate || exit
fi

echo "Running updates for PiClock..."
python3 update.py

echo "Deactivating virtual environment"
deactivate
