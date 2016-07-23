# -*- coding: utf-8 -*-
from GoogleMercatorProjection import LatLng
from PyQt4.QtGui import QColor

wuprefix = 'http://api.wunderground.com/api/'
wulocation = LatLng(52.5074559,13.144557)
noaastream = ''
background = 'images/berlin-at-night-mrwallpaper.jpg'
squares1 = 'images/squares1-kevin.png'
squares2 = 'images/squares2-kevin.png'
icons = 'icons-lightblue'
textcolor = '#bef'
clockface = 'images/clockface3.png'
hourhand = 'images/hourhand.png'
minhand = 'images/minhand.png'
sechand = 'images/sechand.png'

metric = 1  #0 = English, 1 = Metric
radar_refresh = 10      # minutes
weather_refresh = 30    # minutes
wind_degrees = 1         # Wind in degrees instead of cardinal
satellite = 0           # show satellite image (clouds) instead of radar 0 = radar, 1 = satellite

fontattr = ''   # gives all text additional attributes using QT style notation
                # example: fontattr = 'font-weight: bold; '
                
dimcolor = QColor('#000000')    # These are to dim the radar images, if needed.
dimcolor.setAlpha(0)            # see and try Config-Example-Bedside.py

# Language Specific wording
wuLanguage = "DL"   # Weather Undeground Language code (https://www.wunderground.com/weather/api/d/docs?d=language-support&MR=1)
DateLocale = 'de_DE.utf-8'  # The Python Locale for date/time (locale.setlocale)
                            # Locales must be installed in your Pi.. to check what is installed
                            # locale -a
                            # to install locales
                            # sudo dpkg-reconfigure locales
LPressure = "Luftdruck "
LHumidity = "Feuchtigkeit "
LWind = "Wind "
Lgusting = u" böen "
LFeelslike = u"Fühlen "
LPrecip1hr = " Niederschlag 1h:"
LToday = "Teute: "
LSunRise = "Sonnenaufgang:"
LSet = " unter: "
LMoonPhase = " Mond Phase:"
LInsideTemp = "Innen Temp "
 
radar1 = {
    'center' : LatLng(52.5074559,13.144557),
    'zoom' : 7,
    'markers' : (
        {
        'location' : LatLng(52.5074559,13.144557),
        'color' : 'red',
        'size' : 'small',
        },
        )
    }

    
radar2 = {
    'center' : LatLng(52.5074559,13.144557),
    'zoom' : 11,
    'markers' : (
        {
        'location' : LatLng(52.5074559,13.144557),
        'color' : 'red',
        'size' : 'small',
        },
        )
    }

    
radar3 = {
    'center' : LatLng(52.5074559,13.144557),
    'zoom' : 7,
    'markers' : (
        {
        'location' : LatLng(52.5074559,13.144557),
        'color' : 'red',
        'size' : 'small',
        },
        )
    }

radar4 = {
    'center' : LatLng(52.5074559,13.144557),
    'zoom' : 11,
    'markers' : (
        {
        'location' : LatLng(52.5074559,13.144557),
        'color' : 'red',
        'size' : 'small',
        },
        )
    }
