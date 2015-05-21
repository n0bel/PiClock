# PiClock Hardware Guide

## Introduction

I'm going to assume you know how to connect your Raspberry Pi, Power supply, Monitor, 
keyboard/mouse and Wifi or Wired Ethernet.

What follows is the details of various optional hardware you can add to your Raspi
to add features or make your clock cooler.

If you want to experiment and learn about the various hardware, and possibly breadboard
them first, I've included some decent guides for that. *However, you can just skip to the
picture to show the hookup for the PiClock.*

## IR receiver (TSOP4838)

There are many guides showing how to connect an IR receiver (and IR LEDs) to a Raspberry Pi.
Here's one: http://www.raspberry-pi-geek.com/Archive/2014/03/Controlling-your-Pi-with-an-infrared-remote

One thing to note is that most of these use GPIO18 (header pin 12).  The Install instructions I've provided
require the use of **GPIO3 (header pin 5)**.  I've found this more convenient, usually sharing the connector
with the DS18B20 temperature probe on GPIO4 (header pin 7). 

```
Raspi Header Pin           TSOP4838 Pin
3.3V  Pin 1                  Pin 2
Gnd   Pin 9                  Pin 1
GPIO3 Pin 5                  Pin 3
```

[image to be created]

## Inside Temperature ( DS18B20 )

There are many guides showing how to connect and check one or more DS18B20s to
a Raspberry Pi.   Here's one: http://www.modmypi.com/blog/ds18b20-one-wire-digital-temperature-sensor-and-the-raspberry-pi

```
Raspi Header Pin           DS18B20 Pin
3.3V  Pin 1                  Pin 3
Gnd   Pin 9                  Pin 1
GPIO4 Pin 7                  Pin 2
```

[image to be created]


## WS2818b RGB LED AmbiLight strip

A good background guide about how WS2818b connects to the Raspberry Pi can be found here:
https://learn.adafruit.com/neopixels-on-raspberry-pi/overview

You might be tempted to connect the LED strip power to the 5V header pin of the Pi -- just don't!
That pin can't pass enough current.   With all the lights on full you may need an extra 1A to
power the LED string, so size your power supply accordingly.

Everyone seems to recommend a level shift (3.3V to 5V) to drive the LEDs.   I've found this to
be unnecessary.  Your milage may vary.  The data pin of the WS2818b string should be connected
to GPIO18, header pin 12.

[image to be created]

## Buttons



# this guide is not yet complete
