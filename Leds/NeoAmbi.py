#!/usr/bin/python

from NeoPixel import NeoPixel, Color
from time import sleep, time
from math import modf
import colorsys


# from RGB in float 0..1.0 to NeoPixel Color 0..255
def toNeoPixelColor(r, g, b):
    if r > 1:
        r = 1
    if g > 1:
        g = 1
    if b > 1:
        b = 1
    if r < 0:
        r = 0
    if g < 0:
        g = 0
    if b < 0:
        b = 0
    c = Color()
    c.r = int(r * 255)
    c.g = int(g * 255)
    c.b = int(b * 255)
    return(c)

# Creates a rainbow of all colors across all leds
# The rainbow slides around once per minute
if __name__ == "__main__":
    pixels = 27  # how many leds do you have.
    n = NeoPixel(pixels)
    n.setBrightness(1.)
    while(1):
        (fractionOfMinute, dummy) = modf(time() / 60.0)
        for i in range(0, pixels - 1):
            p = i / float(pixels)    # 0.0..1.0 by position on string
            q = p + fractionOfMinute
            while(q > 1):
                q = q - 1.0  # normalize for overflow
            (r, g, b) = colorsys.hsv_to_rgb(q, 1.0, 1.0)
            n.setPixelColor(i, toNeoPixelColor(r, g, b))
        n.show()
        sleep(0.2)
    n.clear()
    n.show()
    del n
    exit(0)
