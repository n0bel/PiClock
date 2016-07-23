from GoogleMercatorProjection import LatLng
from PyQt4.QtGui import QColor

wuprefix = 'http://api.wunderground.com/api/'
wulocation = LatLng(44.9764016,-93.2486732)
noaastream = 'http://audioplayer.wunderground.com:80/tim273/edina'
background = 'images/bb.jpg'
squares1 = 'images/squares1-green.png'
squares2 = 'images/squares2-green.png'
icons = 'icons-darkgreen'
textcolor = '#206225'
clockface = 'images/clockface3-darkgreen.png'
hourhand = 'images/hourhand-darkgreen.png'
minhand = 'images/minhand-darkgreen.png'
sechand = 'images/sechand-darkgreen.png'

metric = 0
radar_refresh = 10
weather_refresh = 30

fontattr = 'font-weight: bold; '
dimcolor = QColor('#103125')
dimcolor.setAlpha(192)

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
