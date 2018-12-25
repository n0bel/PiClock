#!/usr/bin/python
# Must be run under sudo
# Requires: sudo pip install rpi_ws281x

import _rpi_ws281x as ws
from time import sleep, time
from math import modf
import colorsys

# LED configuration.
LED_COUNT = 27         # How many LEDs to light.

# 0..2
LED_CHANNEL = 0

# Frequency of the LED signal. Should be 800khz or 400khz
LED_FREQ_HZ = 800000


# DMA channel to use, can be 0-14.
LED_DMA_NUM = 5

# GPIO connected to the LED signal line. Must support PWM
LED_GPIO = 18

# Set to 0 for darkest and 255 for brightest
LED_BRIGHTNESS = 255

# Set to 1 to invert the LED signal, good if using NPN
# transistor as a 3.3V->5V level converter.  Keep at 0
# for a normal/non-inverted signal.
LED_INVERT = 0


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
    c = ((int(r * 255) & 0xff) << 16 |
         (int(g * 255) & 0xff) << 8 | (int(b * 255) & 0xff))
    return(c)


leds = ws.new_ws2811_t()

channel = ws.ws2811_channel_get(leds, LED_CHANNEL)

ws.ws2811_channel_t_count_set(channel, LED_COUNT)
ws.ws2811_channel_t_gpionum_set(channel, LED_GPIO)
ws.ws2811_channel_t_invert_set(channel, LED_INVERT)
ws.ws2811_channel_t_brightness_set(channel, LED_BRIGHTNESS)

ws.ws2811_t_freq_set(leds, LED_FREQ_HZ)
ws.ws2811_t_dmanum_set(leds, LED_DMA_NUM)

resp = ws.ws2811_init(leds)
if resp != 0:
        raise RuntimeError('ws2811_init failed with code {0}'.format(resp))

try:
    offset = 0
    while True:
        (fractionOfMinute, dummy) = modf(time() / 60.0)
        for i in range(LED_COUNT):
                p = i / float(LED_COUNT)    # 0.0..1.0 by position on string
                q = p + fractionOfMinute
                while(q > 1):
                    q = q - 1.0  # normalize for overflow
                (r, g, b) = colorsys.hsv_to_rgb(q, 1.0, 1.0)
                ws.ws2811_led_set(channel, i, toNeoPixelColor(r, g, b))

        resp = ws.ws2811_render(leds)
        if resp != 0:
            raise RuntimeError('ws2811_render failed with code {0}'.
                               format(resp))

        sleep(0.2)

finally:
    for i in range(LED_COUNT):
        ws.ws2811_led_set(channel, i, 0)
    resp = ws.ws2811_render(leds)
    if resp != 0:
        raise RuntimeError('ws2811_render failed with code {0}'.format(resp))
    ws.ws2811_fini(leds)
    ws.delete_ws2811_t(leds)
