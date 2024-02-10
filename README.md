# PiClock
## PiClock Mods
Fork of PiClock that uses custom dark maps from MapBox, for better contrast 
between the weather radar and the maps, with an additional map overlay so that 
rain/snow clouds do not obscure map information, such as labels, borders, and roads.

The radar windows consist of three layers:
 - Bottom layer is a plain MapBox dark map with no labels, borders, or roads.
 - Middle layer is the weather radar imagery.
 - Top layer is a transparent MapBox map with only labels, borders, and roads.

## Screenshots of PiClock with Dark Maps
![PiClock with dark maps screen 1](Pictures/piclock_dark_maps_screen1.png)

![PiClock with dark maps screen 2](Pictures/piclock_dark_maps_screen2.png)

## Original PiClock
A Fancy Clock built around a monitor and a Raspberry Pi

![PiClock Picture](Pictures/20150307_222711.jpg)

This project started out as a way to waste a Saturday afternoon.
I had a Raspberry Pi and an extra monitor and had just taken down an analog clock from my living room wall.
I was contemplating getting a radio sync'ed analog clock to replace it, so I didn't have to worry about
it being accurate.

But instead the PiClock was born.

The early days and evolution of it are chronicled on my blog:
[NØBEL Blog - Raspberry Pi Clock](http://n0bel.net/v1/index.php/projects/raspberry-pi-clock)

If you want to build your own, I'd suggest starting with the overview:
[Overview of the PiClock](Documentation/Overview.md)

To install the PiClock on your Raspberry Pi, follow these instructions (all the extra hardware (IR Remote, GPIO buttons, Temperature, LEDs) are optional):
[Install Instructions for PiClock](Documentation/Install.md)

If you want to use the PiClock on a different desktop (not your Raspberry Pi), I'd suggest using these instructions:
[Install Instructions for PiClock (Clock Only)](Documentation/Install-Clock-Only.md)

Of course, you can jump to the hardware guide anytime:
[PiClock Hardware Guide](Documentation/Hardware.md)