# -*- coding: utf-8 -*-
from GoogleMercatorProjection import LatLng
from PyQt4.QtGui import QColor

# LOCATION(S)
# Further radar configuration (zoom, marker location) can be
# completed under the RADAR section
primary_coordinates = 52.5074559, 13.144557  # Change to your Lat/Lon

location = LatLng(primary_coordinates[0], primary_coordinates[1])
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


digital = 0             # 1 = Digtal Clock, 0 = Analog Clock

# Goes with light blue config (like the default one)
digitalcolor = "#50CBEB"
digitalformat = "{0:%I:%M\n%S %p}"  # The format of the time
digitalsize = 200
# The above example shows in this way:
#  https://github.com/n0bel/PiClock/blob/master/Documentation/Digital%20Clock%20v1.jpg
# ( specifications of the time string are documented here:
#  https://docs.python.org/2/library/time.html#time.strftime )

# digitalformat = "{0:%I:%M}"
# digitalsize = 250
#  The above example shows in this way:
#  https://github.com/n0bel/PiClock/blob/master/Documentation/Digital%20Clock%20v2.jpg


metric = 1  # 0 = English, 1 = Metric
radar_refresh = 10      # minutes
weather_refresh = 30    # minutes
# Wind in degrees instead of cardinal 0 = cardinal, 1 = degrees
wind_degrees = 0


# gives all text additional attributes using QT style notation
# example: fontattr = 'font-weight: bold; '
fontattr = ''

# These are to dim the radar images, if needed.
# see and try Config-Example-Bedside.py
dimcolor = QColor('#000000')
dimcolor.setAlpha(0)

METAR="EDDB"  # Berlin-Schönefeld International Airport

# Language Specific wording
# DarkSky Language code
#  (https://darksky.net/dev/docs under lang=)
Language = "DE"

# The Python Locale for date/time (locale.setlocale)
#  '' for default Pi Setting
# Locales must be installed in your Pi.. to check what is installed
# locale -a
# to install locales
# sudo dpkg-reconfigure locales
DateLocale = 'de_DE.utf-8'

# Language specific wording
# thanks to colonia27 for the language work
LPressure = "Luftdruck "
LHumidity = "Feuchtigkeit "
LWind = "Wind "
Lgusting = u" böen "
LFeelslike = u"Gefühlt "
LPrecip1hr = " Niederschlag 1h:"
LToday = "Heute: "
LSunRise = "Sonnenaufgang:"
LSet = " unter: "
LMoonPhase = " Mond Phase:"
LInsideTemp = "Innen Temp "
LRain = " Regen: "
LSnow = " Schnee: "
Lmoon1 = 'Neumond'
Lmoon2 = 'Zunehmender Sichelmond'
Lmoon3 = 'Zunehmender Halbmond'
Lmoon4 = 'Zunehmender Dreiviertelmond'
Lmoon5 = 'Vollmond '
Lmoon6 = 'Abnehmender Dreiviertelmond'
Lmoon7 = 'Abnehmender Halbmond'
Lmoon8 = 'Abnehmender Sichelmond'
# Language Specific terms for weather conditions
Lcc_code_map = {
            "freezing_rain_heavy": "Gefrierender Regen",
            "freezing_rain": "Gefrierender Regen",
            "freezing_rain_light": "Gefrierender Regen",
            "freezing_drizzle": "Gefrierender Nieselregen",
            "ice_pellets_heavy": "Eisstücke",
            "ice_pellets": "Eisstücke",
            "ice_pellets_light": "Eisstücke",
            "snow_heavy": "Starker Schneefall",
            "snow": "Schnee",
            "snow_light": "Leichter Schnee",
            "flurries": "Gewitter",
            "tstorm": "Gewitter",
            "rain_heavy": "Starkregen",
            "rain": "Regen",
            "rain_light": "Leichter Regen",
            "drizzle": "Nieselregen",
            "fog_light": "Leichter Nebel",
            "fog": "Nebel",
            "cloudy": "Wolkig",
            "mostly_cloudy": "Meist Wolkig",
            "partly_cloudy": "Teilweise Wolkig",
            "mostly_clear": "Teilweise klar",
            "clear": "Klar"
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
    'zoom': 7,  # this is a google maps zoom factor, bigger = smaller area
    'markers': (   # google maps markers can be overlayed
        {
            'location': primary_location,
            'color': 'red',
            'size': 'small',
        },          # dangling comma is on purpose.
    )
}


radar2 = {
    'center': primary_location,
    'zoom': 11,
    'markers': (
        {
            'location': primary_location,
            'color': 'red',
            'size': 'small',
        },
    )
}


radar3 = {
    'center': primary_location,
    'zoom': 7,
    'markers': (
        {
            'location': primary_location,
            'color': 'red',
            'size': 'small',
        },
    )
}

radar4 = {
    'center': primary_location,
    'zoom': 11,
    'markers': (
        {
            'location': primary_location,
            'color': 'red',
            'size': 'small',
        },
    )
}
