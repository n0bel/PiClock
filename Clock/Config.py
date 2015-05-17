from GoogleMercatorProjection import LatLng

wuprefix = 'http://api.wunderground.com/api/'
wulocation = LatLng(44.7212951,-93.2008627)
noaastream = 'http://audioplayer.wunderground.com:80/tim273/edina'
background = 'images/clockbackground-kevin.png'
background2 = 'images/clockbackground2-kevin.png'
icons = 'icons-lightblue'
textcolor = '#bef'
clockface = 'images/clockface3.png'
hourhand = 'images/hourhand.png'
minhand = 'images/minhand.png'
sechand = 'images/sechand.png'


radar1 = {
    'center' : LatLng(44.7212951,-93.2008627),
    'zoom' : 7,
    'markers' : (
        {
        'location' : LatLng(44.7212951,-93.2008627),
        'color' : 'red',
        'size' : 'small',
        },
        {
        'location' : LatLng(44.280383,-92.983832),
        'color' : 'red',
        'size' : 'small',
        },
        {
        'location' : LatLng(44.276069,-93.289238),
        'color' : 'red',
        'size' : 'small',
        }
        )
    }

    
radar2 = {
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

    
radar3 = {
    'center' : LatLng(44.7212951,-93.2008627),
    'zoom' : 7,
    'markers' : (
        {
        'location' : LatLng(44.7212951,-93.2008627),
        'color' : 'red',
        'size' : 'small',
        },
        {
        'location' : LatLng(44.280383,-92.983832),
        'color' : 'red',
        'size' : 'small',
        },
        {
        'location' : LatLng(44.276069,-93.289238),
        'color' : 'red',
        'size' : 'small',
        }
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
