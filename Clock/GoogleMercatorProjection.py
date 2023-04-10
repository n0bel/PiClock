# http://stackoverflow.com/questions/12507274/how-to-get-bounds-of-a-google-static-map
import math

MERCATOR_RANGE = 256


def bound(value, opt_min, opt_max):
    if opt_min is not None:
        value = max(value, opt_min)
    if opt_max is not None:
        value = min(value, opt_max)
    return value


def degrees_to_radians(deg):
    return deg * (math.pi / 180)


def radians_to_degrees(rad):
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
        self.pixelOrigin_ = Point(int(MERCATOR_RANGE / 2.0), int(MERCATOR_RANGE / 2.0))
        self.pixelsPerLonDegree_ = MERCATOR_RANGE / 360.0
        self.pixelsPerLonRadian_ = MERCATOR_RANGE / (2.0 * math.pi)

    def from_latlng_to_point(self, latlng, opt_point=None):
        point = opt_point if opt_point is not None else Point(0, 0)
        origin = self.pixelOrigin_
        point.x = origin.x + latlng.lng * self.pixelsPerLonDegree_
        # NOTE(appleton): Truncating to 0.9999 effectively limits latitude to
        # 89.189.This is about a third of a tile past the edge of world tile
        siny = bound(math.sin(degrees_to_radians(latlng.lat)), -0.9999, 0.9999)
        point.y = origin.y + 0.5 * math.log((1 + siny) / (1.0 - siny)) * -self.pixelsPerLonRadian_
        return point

    def from_point_to_latlng(self, point):
        origin = self.pixelOrigin_
        lng = (point.x - origin.x) / self.pixelsPerLonDegree_
        lat_radians = (point.y - origin.y) / -self.pixelsPerLonRadian_
        lat = radians_to_degrees(2.0 * math.atan(math.exp(lat_radians)) - math.pi / 2.0)
        return LatLng(lat, lng)


def get_point(point, center, zoom, mapwidth, mapheight):
    scale = 2.0 ** zoom
    proj = MercatorProjection()
    center_p = proj.from_latlng_to_point(center)
    center_p.x = center_p.x * scale
    center_p.y = center_p.y * scale
    subject_p = proj.from_latlng_to_point(point)
    subject_p.x = subject_p.x * scale
    subject_p.y = subject_p.y * scale
    return Point((subject_p.x - center_p.x) + mapwidth / 2.0, (subject_p.y - center_p.y) + mapheight / 2.0)


def get_corners(center, zoom, mapwidth, mapheight):
    scale = 2.0 ** zoom
    proj = MercatorProjection()
    center_px = proj.from_latlng_to_point(center)
    sw_point = Point(center_px.x - (mapwidth / 2.0) / scale, center_px.y + (mapheight / 2.0) / scale)
    sw_lat_lon = proj.from_point_to_latlng(sw_point)
    ne_point = Point(center_px.x + (mapwidth / 2.0) / scale, center_px.y - (mapheight / 2.0) / scale)
    ne_lat_lon = proj.from_point_to_latlng(ne_point)
    return {'N': ne_lat_lon.lat, 'E': ne_lat_lon.lng, 'S': sw_lat_lon.lat, 'W': sw_lat_lon.lng, }


# https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames

def get_tile_xy(latlng, zoom):
    lat_rad = math.radians(latlng.lat)
    n = 2.0 ** zoom
    xtile = (latlng.lng + 180.0) / 360.0 * n
    ytile = ((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return {'X': xtile, 'Y': ytile}
