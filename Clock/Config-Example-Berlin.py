# -*- coding: utf-8 -*-
from PyQt5.QtGui import QColor

from GoogleMercatorProjection import LatLng  # NOQA

# LOCATION(S)
# Further radar configuration (zoom, marker location) can be
# completed under the RADAR section
primary_coordinates = 52.5074559, 13.144557  # Change to your Lat/Lon

# Location for weather report
location = LatLng(primary_coordinates[0], primary_coordinates[1])
# Default radar location
primary_location = LatLng(primary_coordinates[0], primary_coordinates[1])
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

# SlideShow
useslideshow = 0  # 1 to enable, 0 to disable
slide_time = 305  # in seconds, 3600 per hour
slides = 'images/slideshow'  # the path to your local images
slide_bg_color = '#000'  # https://htmlcolorcodes.com/  black #000

digital = 0  # 1 = Digital Clock, 0 = Analog Clock

# Goes with light blue config (like the default one)
digitalcolor = '#50CBEB'
digitalformat = '{0:%I:%M\n%S %p}'  # Format of the digital clock face
digitalsize = 200

# The above example shows in this way:
#  https://github.com/n0bel/PiClock/blob/master/Documentation/Digital%20Clock%20v1.jpg
# (specifications of the time string are documented here:
#  https://docs.python.org/2/library/time.html#time.strftime)

# digitalformat = '{0:%I:%M}'
# digitalsize = 250
# The above example shows in this way:
# https://github.com/n0bel/PiClock/blob/master/Documentation/Digital%20Clock%20v2.jpg

digitalformat2 = '{0:%H:%M:%S}'  # Format of the digital time on second screen

# Mapbox map styles, need API key (mbapi in ApiKeys.py)
# If no Mapbox API is set, Google Maps are used
map_base = 'bcurley/cj712peyz0bwr2sqfndbggupb'  # Custom dark Mapbox style for land and water only (bottom layer that goes below weather radar)
map_overlay = 'bcurley/cj712r01c0bw62rm9isme3j8c'  # Custom Mapbox style for labels, roads, and borders only (top layer that goes above weather radar)
# map_base = 'mapbox/satellite-streets-v12'  # Uncomment for standard Mapbox Satellite Streets style, and comment/remove the custom style
# map_base = 'mapbox/streets-v12'  # Uncomment for standard Mapbox Streets style, and comment/remove the custom style
# map_base = 'mapbox/outdoors-v12'  # Uncomment for standard Mapbox Outdoors style, and comment/remove the custom style
# map_base = 'mapbox/dark-v11'  # Uncomment for standard Mapbox Dark style, and comment/remove the custom style
# map_overlay = ''  # Uncomment and leave blank if using standard Mapbox style, and comment/remove the custom style

# For more Mapbox styles, see https://docs.mapbox.com/api/maps/styles/
# To create custom Mapbox styles, sign-in at https://studio.mapbox.com/
# Example: If static map URL is
# https://api.mapbox.com/styles/v1/mapbox/streets-v12/static/-80.2,25.8,10/600x400?access_token=YOUR-ACCESS-TOKEN
# use the portion between '/styles/v1/' and '/static/'
# Standard Mapbox maps will look like 'mapbox/streets-v12'
# User created Mapbox maps will look like 'user-name/map-identifier'

metric = 1  # 0 = English, 1 = Metric
radar_refresh = 10  # minutes
weather_refresh = 30  # minutes
# Wind in degrees instead of cardinal 0 = cardinal, 1 = degrees
wind_degrees = 0

# gives all text additional attributes using QT style notation
# example: fontattr = 'font-weight: bold; '
fontattr = ''

# These are to dim the radar images, if needed.
# see and try Config-Example-Bedside.py
dimcolor = QColor('#000000')
dimcolor.setAlpha(0)

# Optional Current conditions replaced with observations from a METAR station
# METAR is worldwide, provided mostly for pilots
# But data can be sparse outside US and Europe
# If you're close to an international airport, you should find something close
# Find the closest METAR station with the following URL
# https://www.aviationweather.gov/metar
# scroll/zoom the map to find your closest station
# or look up the ICAO code here:
# https://airportcodes.aero/name
METAR = ''

# Language specific wording
# Language code
Language = 'DE'

# The Python Locale for date/time (locale.setlocale)
#  '' for default Pi Setting
# Locales must be installed in your Pi. To check what is installed:
# locale -a
# to install locales
# sudo dpkg-reconfigure locales
DateLocale = 'de_DE.utf-8'

# Language specific wording
# thanks to colonia27 for the language work
LPressure = 'Luftdruck '
LHumidity = 'Feuchtigkeit '
LWind = 'Wind '
Lgusting = u' böen '
LFeelslike = u'Gefühlt '
LPrecip1hr = ' Niederschlag 1h:'
LToday = 'Heute: '
LSunRise = 'Sonnenaufgang:'
LSet = ' unter:'
LMoonPhase = ' Mond Phase:'
LInsideTemp = 'Innen Temp '
LRain = ' Regen: '
LSnow = ' Schnee: '
Lmoon1 = 'Neumond'
Lmoon2 = 'Zunehmender Sichelmond'
Lmoon3 = 'Zunehmender Halbmond'
Lmoon4 = 'Zunehmender Dreiviertelmond'
Lmoon5 = 'Vollmond'
Lmoon6 = 'Abnehmender Dreiviertelmond'
Lmoon7 = 'Abnehmender Halbmond'
Lmoon8 = 'Abnehmender Sichelmond'

# Language specific terms for Tomorrow.io weather conditions
Ltm_code_map = {
    0: 'Unknown',
    1000: 'Klar',
    1100: 'Teilweise klar',
    1101: 'Teilweise Wolkig',
    1102: 'Meist Wolkig',
    1001: 'Wolkig',
    2000: 'Nebel',
    2100: 'Leichter Nebel',
    4000: 'Nieselregen',
    4001: 'Rain',
    4200: 'Light Rain',
    4201: 'Heavy Rain',
    5000: 'Regen',
    5001: 'Gewitter',
    5100: 'Leichter Schnee',
    5101: 'Starker Schneefall',
    6000: 'Gefrierender Nieselregen',
    6001: 'Gefrierender Regen',
    6200: 'Gefrierender Regen',
    6201: 'Gefrierender Regen',
    7000: 'Eisstücke',
    7101: 'Eisstücke',
    7102: 'Eisstücke',
    8000: 'Gewitter'
}

# RADAR
# By default, primary_location entered will be the
#  center and marker of all radar images.
# To update centers/markers, change radar sections
# below the desired lat/lon as:
# -FROM-
# primary_location,
# -TO-
# LatLng(44.9764016,-93.2486732),
radar1 = {
    'center': primary_location,  # the center of your radar block
    'zoom': 7,  # this is a maps zoom factor, bigger = smaller area
    'basemap': map_base,  # Mapbox style for standard map or custom map with land and water only
    'overlay': map_overlay,  # Mapbox style for labels, roads, and borders only
    'color': 6,  # rainviewer radar color style:
    # https://www.rainviewer.com/api.html#colorSchemes
    'smooth': 1,  # rainviewer radar smoothing
    'snow': 1,  # rainviewer radar show snow as different color
    'markers': (  # google maps markers can be overlaid
        {
            'visible': 1,  # 0 = hide marker, 1 = show marker
            'location': primary_location,
            'color': 'red',
            'size': 'small',
            'image': 'teardrop-dot',  # optional image from the markers folder
        },  # dangling comma is on purpose.
    )
}

radar2 = {
    'center': primary_location,
    'zoom': 11,
    'basemap': map_base,
    'overlay': map_overlay,
    'color': 6,
    'smooth': 1,
    'snow': 1,
    'markers': (
        {
            'visible': 1,
            'location': primary_location,
            'color': 'red',
            'size': 'small',
            'image': 'teardrop-dot',
        },
    )
}

radar3 = {
    'center': primary_location,
    'zoom': 7,
    'basemap': map_base,
    'overlay': map_overlay,
    'color': 6,
    'smooth': 1,
    'snow': 1,
    'markers': (
        {
            'visible': 1,
            'location': primary_location,
            'color': 'red',
            'size': 'small',
            'image': 'teardrop-dot',
        },
    )
}

radar4 = {
    'center': primary_location,
    'zoom': 11,
    'basemap': map_base,
    'overlay': map_overlay,
    'color': 6,
    'smooth': 1,
    'snow': 1,
    'markers': (
        {
            'visible': 1,
            'location': primary_location,
            'color': 'red',
            'size': 'small',
            'image': 'teardrop-dot',
        },
    )
}
