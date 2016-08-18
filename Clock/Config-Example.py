from GoogleMercatorProjection import LatLng
from PyQt4.QtGui import QColor


# LOCATION(S) 
# Further radar configuration (zoom, marker location) can be completed under the RADAR section
primary_coordinates = 44.9764016,-93.2486732 # Change to your Lat/Lon

wuprefix = 'http://api.wunderground.com/api/'
wulocation = LatLng(primary_coordinates[0],primary_coordinates[1]) # Location for weather report
primary_location = LatLng(primary_coordinates[0],primary_coordinates[1]) # Default radar location
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
satellite = 0           # Depreciated: use 'satellite' key in radar section, on a per radar basis
                        # if this is used, all radar blocks will get satellite images
                        
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


# RADAR
# By default, primary_location entered will be the center and marker of all radar images.
# To update centers/markers, change radar sections below the desired lat/lon as:
# -FROM-
# primary_location,
# -TO-
# LatLng(44.9764016,-93.2486732),
radar1 = {
    'center' : primary_location,  # the center of your radar block
    'zoom' : 7, # this is a google maps zoom factor, bigger = smaller area
    'satellite' : 0,    # 1 => show satellite images instead of radar (colorized IR images)
    'markers' : (   # google maps markers can be overlayed
        {
        'location' : primary_location, 
        'color' : 'red',
        'size' : 'small',
        },          # dangling comma is on purpose.
        )
    }

    
radar2 = {
    'center' : primary_location,
    'zoom' : 11,
    'satellite' : 0,
    'markers' : (
        {
        'location' : primary_location, 
        'color' : 'red',
        'size' : 'small',
        },
        )
    }

    
radar3 = {
    'center' : primary_location, 
    'zoom' : 7,
    'satellite' : 0,
    'markers' : (
        {
        'location' : primary_location, 
        'color' : 'red',
        'size' : 'small',
        },
        )
    }

radar4 = {
    'center' : primary_location, 
    'zoom' : 11,
    'satellite' : 0,
    'markers' : (
        {
        'location' : primary_location, 
        'color' : 'red',
        'size' : 'small',
        },
        )
    }
