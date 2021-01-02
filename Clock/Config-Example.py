from GoogleMercatorProjection import LatLng
from PyQt4.QtGui import QColor


# LOCATION(S)
# Further radar configuration (zoom, marker location) can be
# completed under the RADAR section
primary_coordinates = 44.9764016, -93.2486732  # Change to your Lat/Lon

location = LatLng(primary_coordinates[0], primary_coordinates[1])
primary_location = LatLng(primary_coordinates[0], primary_coordinates[1])
noaastream = 'http://www.urberg.net:8000/tim273/edina'
background = 'images/clockbackground-kevin.png'
squares1 = 'images/squares1-kevin.png'
squares2 = 'images/squares2-kevin.png'
icons = 'icons-lightblue'
textcolor = '#bef'
clockface = 'images/clockface3.png'
hourhand = 'images/hourhand.png'
minhand = 'images/minhand.png'
sechand = 'images/sechand.png'

# SlideShow
useslideshow = 0             # 1 to enable, 0 to disable
slide_time = 305              # in seconds, 3600 per hour
slides = 'images/slideshow'   # the path to your local images
slide_bg_color = "#000"       # https://htmlcolorcodes.com/  black #000

digital = 0                 # 1 = Digtal Clock, 0 = Analog Clock

# Goes with light blue config (like the default one)
digitalcolor = "#50CBEB"
digitalformat = "{0:%I:%M\n%S %p}"  # Format of the digital clock face
digitalsize = 200

# The above example shows in this way:
#  https://github.com/n0bel/PiClock/blob/master/Documentation/Digital%20Clock%20v1.jpg
# ( specifications of the time string are documented here:
#  https://docs.python.org/2/library/time.html#time.strftime )

# digitalformat = "{0:%I:%M}"
# digitalsize = 250
#  The above example shows in this way:
#  https://github.com/n0bel/PiClock/blob/master/Documentation/Digital%20Clock%20v2.jpg

digitalformat2 = "{0:%H:%M:%S}"  # Format of the digital time on second screen

usemapbox = 0   # Use Mapbox.com for maps, needs api key (mbapi in ApiKeys.py)
metric = 0  # 0 = English, 1 = Metric
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

# Optional Current conditions replaced with observations from a METAR station
# METAR is world wide, provided mostly for pilots
# But data can be sparse outside US and Europe
#  If you're close to an international airport, you should find soemthing close
# Find the closest METAR station with the following URL
# https://www.aviationweather.gov/metar
# scroll/zoom the map to find your closest station
# or look up the ICAO code here:
# https://airportcodes.aero/name
METAR = ''

# Language Specific wording
# DarkSky Language code
#  (https://darksky.net/dev/docs under lang=)
Language = "EN"

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
Lgusting = " gust "
LFeelslike = "Feels like "
LPrecip1hr = " Precip 1hr: "
LToday = "Today: "
LSunRise = "Sun Rise: "
LSet = " Set: "
LMoonPhase = " Moon: "
LInsideTemp = "Inside Temp "
LRain = " Rain: "
LSnow = " Snow: "
Lmoon1 = 'New Moon'
Lmoon2 = 'Waxing Crescent'
Lmoon3 = 'First Quarter'
Lmoon4 = 'Waxing Gibbous'
Lmoon5 = 'Full Moon'
Lmoon6 = 'Waning Gibbous'
Lmoon7 = 'Third Quarter'
Lmoon8 = 'Waning Crecent'
# Language Specific terms for weather conditions
Lcc_code_map = {
            "freezing_rain_heavy": "Freezing Rain",
            "freezing_rain": "Freezing Rain",
            "freezing_rain_light": "Freezing Rain",
            "freezing_drizzle": "Freezing Drizzle",
            "ice_pellets_heavy": "Ice Pellets",
            "ice_pellets": "Ice Pellets",
            "ice_pellets_light": "Ice Pellets",
            "snow_heavy": "Heavy Snow",
            "snow": "Snow",
            "snow_light": "Light Snow",
            "flurries": "Flurries",
            "tstorm": "Thunder Storm",
            "rain_heavy": "Heavy Rain",
            "rain": "Rain",
            "rain_light": "Light Rain",
            "drizzle": "Drizzle",
            "fog_light": "Light Fog",
            "fog": "Fog",
            "cloudy": "Cloudy",
            "mostly_cloudy": "Mostly Cloudy",
            "partly_cloudy": "Partly Cloudy",
            "mostly_clear": "Mostly Clear",
            "clear": "Clear"
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
    'style': 'mapbox/satellite-streets-v10',  # optional style (mapbox only)
    'color': 6,  # rainviewer radar color style:
                 # https://www.rainviewer.com/api.html#colorSchemes
    'smooth': 1,  # rainviewer radar smoothing
    'snow': 1,  # rainviewer radar show snow as different color
    'markers': (   # google maps markers can be overlayed
        {
            'visible': 1,  # 0 = hide marker, 1 = show marker
            'location': primary_location,
            'color': 'red',
            'size': 'small',
            'image': 'teardrop-dot',  # optional image from the markers folder
        },          # dangling comma is on purpose.
    )
}


radar2 = {
    'center': primary_location,
    'zoom': 11,
    'style': 'mapbox/satellite-streets-v10',
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
    'style': 'mapbox/satellite-streets-v10',
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
    'style': 'mapbox/satellite-streets-v10',
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
