# http://stackoverflow.com/questions/12507274/how-to-get-bounds-of-a-google-static-map
import math
MERCATOR_RANGE = 256


def bound(value, opt_min, opt_max):
    if (opt_min is not None):
        value = max(value, opt_min)
    if (opt_max is not None):
        value = min(value, opt_max)
    return value


def degreesToRadians(deg):
    return deg * (math.pi / 180)


def radiansToDegrees(rad):
    return rad / (math.pi / 180)


class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __repr__(self):
        return "Point(%d,%d)" % (self.x, self.y)

    def __str__(self):
        return "(x=%d,y=%d)" % (self.x, self.y)


class LatLng:
    def __init__(self, lt, ln):
        self.lat = lt
        self.lng = ln

    def __repr__(self):
        return "LatLng(%g,%g)" % (self.lat, self.lng)

    def __str__(self):
        return "(lat=%g,lng=%g)" % (self.lat, self.lng)


class MercatorProjection:

    def __init__(self):
        self.pixelOrigin_ = Point(MERCATOR_RANGE / 2.0, MERCATOR_RANGE / 2.0)
        self.pixelsPerLonDegree_ = MERCATOR_RANGE / 360.0
        self.pixelsPerLonRadian_ = MERCATOR_RANGE / (2.0 * math.pi)

    def fromLatLngToPoint(self, latLng, opt_point=None):
        point = opt_point if opt_point is not None else Point(0, 0)
        origin = self.pixelOrigin_
        point.x = origin.x + latLng.lng * self.pixelsPerLonDegree_
        # NOTE(appleton): Truncating to 0.9999 effectively limits latitude to
        # 89.189.This is about a third of a tile past the edge of the world tile
        siny = bound(math.sin(degreesToRadians(latLng.lat)), -0.9999, 0.9999)
        point.y = origin.y + 0.5 * math.log((1 + siny) / (1.0 - siny)) * \
            -self.pixelsPerLonRadian_
        return point

    def fromPointToLatLng(self, point):
        origin = self.pixelOrigin_
        lng = (point.x - origin.x) / self.pixelsPerLonDegree_
        latRadians = (point.y - origin.y) / -self.pixelsPerLonRadian_
        lat = radiansToDegrees(2.0 * math.atan(math.exp(latRadians)) -
                               math.pi / 2.0)
        return LatLng(lat, lng)

# pixelCoordinate = worldCoordinate * pow(2,zoomLevel)


def getCorners(center, zoom, mapWidth, mapHeight):
    scale = 2.0**zoom
    proj = MercatorProjection()
    centerPx = proj.fromLatLngToPoint(center)
    SWPoint = Point(centerPx.x - (mapWidth / 2.0) / scale, centerPx.y +
                    (mapHeight / 2.0) / scale)
    SWLatLon = proj.fromPointToLatLng(SWPoint)
    NEPoint = Point(centerPx.x + (mapWidth / 2.0) / scale, centerPx.y -
                    (mapHeight / 2.0) / scale)
    NELatLon = proj.fromPointToLatLng(NEPoint)
    return {
        'N': NELatLon.lat,
        'E': NELatLon.lng,
        'S': SWLatLon.lat,
        'W': SWLatLon.lng,
    }
