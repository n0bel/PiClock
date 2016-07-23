from GoogleMercatorProjection import LatLng

wuprefix = 'http://api.wunderground.com/api/'
wulocation = LatLng(51.5286416,-0.1015987)
noaastream = '???'
background = 'images/london-at-night-wallpapers.jpg'
squares1 = 'images/squares1-kevin.png'
squares2 = 'images/squares2-kevin.png'
icons = 'icons-lightblue'
textcolor = '#bef'
clockface = 'images/clockface3.png'
hourhand = 'images/hourhand.png'
minhand = 'images/minhand.png'
sechand = 'images/sechand.png'

metric = 1  #0 = English, 1 = Metric

radar1 = {
    'center' : LatLng(51.5286416,-0.1015987),
    'zoom' : 7,
    'markers' : (
        {
        'location' : LatLng(51.5286416,-0.1015987),
        'color' : 'red',
        'size' : 'small',
        },
        )
    }

    
radar2 = {
    'center' : LatLng(51.5286416,-0.1015987),
    'zoom' : 11,
    'markers' : (
        {
        'location' : LatLng(51.5286416,-0.1015987),
        'color' : 'red',
        'size' : 'small',
        },
        )
    }

    
radar3 = {
    'center' : LatLng(51.5286416,-0.1015987),
    'zoom' : 7,
    'markers' : (
        {
        'location' : LatLng(51.5286416,-0.1015987),
        'color' : 'red',
        'size' : 'small',
        },
        )
    }

radar4 = {
    'center' : LatLng(51.5286416,-0.1015987),
    'zoom' : 11,
    'markers' : (
        {
        'location' : LatLng(51.5286416,-0.1015987),
        'color' : 'red',
        'size' : 'small',
        },
        )
    }
