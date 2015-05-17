

import RPi.GPIO as GPIO
import time
import os.path

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

if not os.path.isfile("/sys/class/gpio/gpio23/value"):
	f = open("/sys/class/gpio/export","w")
	f.write("23")
	f.close()

f = open("/sys/class/gpio/gpio23/direction","w")
f.write("in\n")
f.close()

