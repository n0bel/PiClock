from MercatorProjection import LatLng
from PyQt4.QtGui import QColor


# LOCATION(S)
# Further radar configuration (zoom, marker location) can be
# completed under the RADAR section
primary_coordinates = 25.761680, -80.191790  # Change to your Lat/Lon

# Map layers for radar
# Sign-in and create custom map styles at https://www.mapbox.com/studio/styles/
# Example: If static map URL is 
# https://api.mapbox.com/styles/v1/mapbox/streets-v10/static/-80.2,25.8,10/600x400?access_token=YOUR-ACCESS-TOKEN
# use the portion between '/styles/v1/' and '/static/'
# Standard Mapbox maps will look like 'mapbox/streets-v10'
# User created Mapbox maps will look like 'user-name/map-identifier'
map_base = 'bcurley/cj712peyz0bwr2sqfndbggupb'  # Mapbox style for land and water only (bottom layer that goes below weather radar)
map_overlay = 'bcurley/cj712r01c0bw62rm9isme3j8c'  # Mapbox style for labels, roads, borders, and markers only (top layer that goes above weather radar)

# NOAA Weather Radio stream
# Find mp3 by viewing source of web page at http://noaaweatherradio.org/
noaastream = 'https://www.weather.gov/media/mfl/nwr/MIAZFPMIA.mp3'

# Weather conditions source from Weather Underground
wuPWS = 1    # 1 = use Personal Weather Stations (default), 0 = use National Weather Service

wuprefix = 'http://api.wunderground.com/api/'
wulocation = LatLng(primary_coordinates[0], primary_coordinates[1])  # Location for weather report
primary_location = LatLng(primary_coordinates[0], primary_coordinates[1])  # Default radar location
background = 'images/clockbackground-kevin.png'
squares1 = 'images/squares1-kevin.png'
squares2 = 'images/squares2-kevin.png'
icons = 'icons-lightblue'
textcolor = '#bef'
clockface = 'images/clockface3.png'
hourhand = 'images/hourhand.png'
minhand = 'images/minhand.png'
sechand = 'images/sechand.png'


# Clock display
digital = 0    # 1 = Digtal Clock, 0 = Analog Clock

# Goes with light blue config (like the default one)
digitalcolor = "#50CBEB"
digitalformat = "{0:%I:%M\n%S %p}"  # The format of the digital time on primary screen
digitalformat2 = "{0:%I:%M:%S %p}"  # The format of the digital time on secondary screen
digitalsize = 200  # Size of digital time display on primary screen
# The above example shows in this way:
# https://github.com/n0bel/PiClock/blob/master/Documentation/Digital%20Clock%20v1.jpg
# Specifications of the time string are documented here:
# https://docs.python.org/2/library/time.html#time.strftime

# digitalformat = "{0:%I:%M}"
# digitalformat2 = "{0:%I:%M}"
# digitalsize = 200
# The above example shows in this way:
# https://github.com/n0bel/PiClock/blob/master/Documentation/Digital%20Clock%20v2.jpg


metric = 0  # 0 = English, 1 = Metric
radar_refresh = 10      # minutes
weather_refresh = 30    # minutes
# Wind in degrees instead of cardinal 0 = cardinal, 1 = degrees
wind_degrees = 0
# Depreciated: use 'satellite' key in radar section, on a per radar basis
# if this is used, all radar blocks will get satellite images
satellite = 0

# gives all text additional attributes using QT style notation
# example: fontattr = 'font-weight: bold; '
fontattr = ''

# These are to dim the radar images, if needed.
# see and try Config-Example-Bedside.py
dimcolor = QColor('#000000')
dimcolor.setAlpha(0)

# Language Specific wording
# Weather Undeground Language code
# https://www.wunderground.com/weather/api/d/docs?d=language-support&MR=1
wuLanguage = "EN"

# The Python Locale for date/time (locale.setlocale)
#  '' for default Pi Setting
# Locales must be installed in your Pi.. to check what is installed
# locale -a
# to install locales
# sudo dpkg-reconfigure locales
DateLocale = ''

# Language specific wording
LPressure = "Pressure "
LHumidity = "Humidity "
LWind = "Wind "
Lgusting = " gusting "
LFeelslike = "Feels like "
LPrecip1hr = " Precip 1hr: "
LToday = "Today: "
LSunRise = "Sun Rise: "
LSet = " Set: "
LMoonPhase = " Moon Phase: "
LInsideTemp = "Inside Temp "
LRain = " Rain: "
LSnow = " Snow: "


# RADAR
# By default, primary_location entered will be the
#  center and marker of all radar images.
# To update centers/markers, change radar sections below the desired lat/lon as:
# -FROM-
# primary_location,
# -TO-
# LatLng(44.9764016,-93.2486732),
radar1 = {
    'center': primary_location,  # the center of your radar block
    'zoom': 5,  # map zoom factor, bigger = smaller area
    'satellite': 0,    # 1 => show satellite images (colorized IR images)
    'basemap': map_base,  # Mapbox style for land and water only
    'overlay': map_overlay,  # Mapbox style for labels, roads, borders, and markers only
    'markers': (   # map markers can be overlayed
        {
            'location': primary_location,
            'shape': 'pin-s',  # Marker shape and size. Options are pin-s, pin-m, pin-l ( '' to hide marker)
            'symbol': 'home',  # Optional Maki symbol https://www.mapbox.com/maki-icons/ ( '' for default pin symbol)
            'color': '008',  # Optional 3 or 6 digit hexadecimal color code ( '' for default color)
        },          # dangling comma is on purpose.
    )
}

radar2 = {
    'center': primary_location,
    'zoom': 7,
    'satellite': 0,
    'basemap': map_base,
    'overlay': map_overlay,
    'markers': (
        {
            'location': primary_location,
            'shape': 'pin-s',
            'symbol': 'home',
            'color': '008',
        },
    )
}


radar3 = {
    'center': primary_location,
    'zoom': 7,
    'satellite': 0,
    'basemap': map_base,
    'overlay': map_overlay,
    'markers': (
        {
            'location': primary_location,
            'shape': 'pin-s',
            'symbol': 'home',
            'color': '008',
        },
    )
}

radar4 = {
    'center': primary_location,
    'zoom': 11,
    'satellite': 0,
    'basemap': map_base,
    'overlay': map_overlay,
    'markers': (
        {
            'location': primary_location,
            'shape': 'pin-s',
            'symbol': 'home',
            'color': '008',
        },
    )
}
