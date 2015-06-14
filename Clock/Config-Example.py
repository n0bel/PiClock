from GoogleMercatorProjection import LatLng

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
