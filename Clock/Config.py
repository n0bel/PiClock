# -*- coding: utf-8 -*-

from GoogleMercatorProjection import LatLng     # NOQA
from PyQt5.QtGui import QColor


# LOCATION(S)
# Further radar configuration (zoom, marker location) can be
# completed under the RADAR section
primary_coordinates = 56.279109, 44.078438   # Change to your Lat/Lon

location = LatLng(primary_coordinates[0], primary_coordinates[1])
primary_location = LatLng(primary_coordinates[0], primary_coordinates[1])
noaastream = '???'
background = 'images/clockbackground-kevin.png'
squares1 = 'images/squares1-kevin.png'
squares2 = 'images/squares2-kevin.png'
icons = 'icons-lightblue'
textcolor = '#bef'
clockface = 'images/clockface3.png'
hourhand = 'images/hourhand.png'
minhand = 'images/minhand.png'
sechand = 'images/sechand.png'

useslideshow = 0
slides = 'images/slideshow'
slide_bg_color = '000000'
slide_time = 60

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

usemapbox = 1  # Use Mapbox.com for maps, needs api key (mbapi in ApiKeys.py)
map_base = 'bcurley/cj712peyz0bwr2sqfndbggupb'  # Custom dark Mapbox style for land and water only (bottom layer that goes below weather radar)
map_overlay = 'bcurley/cj712r01c0bw62rm9isme3j8c'  # Custom Mapbox style for labels, roads, and borders only (top layer that goes above weather radar)

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

METAR = ''
# Language Specific wording
# DarkSky Language code
#  (https://darksky.net/dev/docs under lang=)
Language = "RU"

# The Python Locale for date/time (locale.setlocale)
#  '' for default Pi Setting
# Locales must be installed in your Pi.. to check what is installed
# locale -a
# to install locales
# sudo dpkg-reconfigure locales
DateLocale = 'ru_RU'

# Language specific wording
LPressure = "Давление "
LHumidity = "Влажность "
LWind = "Ветер "
Lgusting = " до "
LFeelslike = "По ощущениям "
LPrecip1hr = " Осадки за час:"
LToday = "Сегодня: "
LSunRise = "Восход: "
LSet = " Заход "
LMoonPhase = " Луна: "
LInsideTemp = "Inside Temp "
LRain = " Дождь: "
LSnow = " Снег: "
Lmoon1 = 'Новолуние'
Lmoon2 = 'Молодая'
Lmoon3 = 'Первая четверть'
Lmoon4 = 'Прибывающая'
Lmoon5 = 'Полнолуние'
Lmoon6 = 'Убывающая'
Lmoon7 = 'Последняя четверть'
Lmoon8 = 'Старая'

# Language specific terms for Tomorrow.io weather conditions
Ltm_code_map = {
    0: 'Нет данных',
    1000: 'Ясно, солнечно',
    1100: 'Ясно',
    1101: 'Безоблачно',
    1102: 'Облачно с прояснениями',
    1001: 'Облачно',
    2000: 'Туман',
    2100: 'Дымка',
    4000: 'Изморось',
    4001: 'Дождь',
    4200: 'Временами дождь',
    4201: 'Ливень',
    5000: 'Снег',
    5001: 'Flurries',
    5100: 'Light Snow',
    5101: 'Heavy Snow',
    6000: 'Freezing Drizzle',
    6001: 'Freezing Rain',
    6200: 'Light Freezing Rain',
    6201: 'Heavy Freezing Rain',
    7000: 'Ice Pellets',
    7101: 'Heavy Ice Pellets',
    7102: 'Light Ice Pellets',
    8000: 'Гроза'
}

# RADAR
# By default, primary_location entered will be the
#  center and marker of all radar images.
# To update centers/markers,change radar sections below the desired lat/lon as:
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
