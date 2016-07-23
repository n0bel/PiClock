from GoogleMercatorProjection import LatLng
from PyQt4.QtGui import QColor

wuprefix = 'http://api.wunderground.com/api/'
wulocation = LatLng(44.9764016,-93.2486732)
noaastream = 'http://audioplayer.wunderground.com:80/tim273/edina'
background = 'images/clockbackground-kevin.png'
squares1 = 'images/squares1-kevin.png'
squares2 = 'images/squares2-kevin.png'
icons = 'icons-lightblue'
textcolor = '#bef'
clockface = 'images/clockface3.png'
hourhand = 'images/hourhand.png'
minhand = 'images/minhand.png'
sechand = 'images/sechand.png'

metric = 0  #0 = English, 1 = Metric
radar_refresh = 10      # minutes
weather_refresh = 30    # minutes
wind_degrees = 0        # Wind in degrees instead of cardinal 0 = cardinal, 1 = degrees
satellite = 0           # show satellite image (clouds) instead of radar 0 = radar, 1 = satellite

fontattr = ''   # gives all text additional attributes using QT style notation
                # example: fontattr = 'font-weight: bold; '
                
dimcolor = QColor('#000000')    # These are to dim the radar images, if needed.
dimcolor.setAlpha(0)            # see and try Config-Example-Bedside.py

# Language Specific wording
wuLanguage = "EN"   # Weather Undeground Language code (https://www.wunderground.com/weather/api/d/docs?d=language-support&MR=1)
DateLocale = ''  # The Python Locale for date/time (locale.setlocale) -- '' for default Pi Setting
                            # Locales must be installed in your Pi.. to check what is installed
                            # locale -a
                            # to install locales
                            # sudo dpkg-reconfigure locales
LPressure = "Pressure "
LHumidity = "Humidity "
LWind = "Wind "
Lgusting = " gusting "
LFeelslike = "Feels like "
LPrecip1hr = " Precip 1hr:"
LToday = "Today: "
LSunRise = "Sun Rise:"
LSet = " Set: "
LMoonPhase = " Moon Phase:"
LInsideTemp = "Inside Temp "
LRain = " Rain: "
LSnow = " Snow: "

radar1 = {
    'center' : LatLng(44.9764016,-93.2486732),
    'zoom' : 7,
    'markers' : (
        {
        'location' : LatLng(44.9764016,-93.2486732),
        'color' : 'red',
        'size' : 'small',
        },
        )
    }

    
radar2 = {
    'center' : LatLng(44.9764016,-93.2486732),
    'zoom' : 11,
    'markers' : (
        {
        'location' : LatLng(44.9764016,-93.2486732),
        'color' : 'red',
        'size' : 'small',
        },
        )
    }

    
radar3 = {
    'center' : LatLng(44.9764016,-93.2486732),
    'zoom' : 7,
    'markers' : (
        {
        'location' : LatLng(44.9764016,-93.2486732),
        'color' : 'red',
        'size' : 'small',
        },
        )
    }

radar4 = {
    'center' : LatLng(44.7212951,-93.2008627),
    'zoom' : 11,
    'markers' : (
        {
        'location' : LatLng(44.7212951,-93.2008627),
        'color' : 'red',
        'size' : 'small',
        },
        )
    }
