import math
from math import sin, cos, tan, acos, pi, radians, log, sqrt

EARTH_RADIUS = 6378137
MERCATOR = "mercator"
LAMBERTAZIMUTAL = "lambert_azimuthal_equal_area"
WINKEL_TRIPEL = "winkel_tripel"
AZIMUTAL_EQUIDISTANT = "azimuthal_equidistant"


def azimuthal_equidistant(lon, lat):
    """
    Transforms coordinates from GPS(WSG84) to Azimuthal (WIP)
    """
    x = lat * math.sin(lon)
    y = -lat * math.cos(lon)
    return x, y


def mercator(lon, lat, rf=1.0 / 1000000.0, lon0=0, max_lat=85, min_lat=-89):
    """Returns Mercator cartesian coodinates from GPS coordinates
    lon -- GPS longitude coordinate given in degrees
    lat -- GPS latitude coordinate given in degrees
    lon0 -- Arbitrary central meridian. Default is Greenwich
    rf - Representative Factor (scale)
    ----
    """
    lon_rad, lat_rad = radians(lon), radians(lat)
    r = rf * EARTH_RADIUS
    x = r * (lon_rad - lon0)
    y = r * log(tan(pi / 4.0 + lat_rad / 2.0))
    if lat < min_lat:
        return x, -20.26181
    return x, y


def winkel_tripel(lon, lat, lon0=0):
    """
    Returns Winkel Tripel coordinates from GPS coordinates

    Arguments:
    lon -- GPS longitude coordinate given in degrees
    lat -- GPS latitude coordinate given in degrees
    lon0 -- Arbitrary central meridian. Default is Greenwich
    RF - Representative Factor (scale)
    """
    lon, lat = radians(lon), radians(lat)
    lon = lon - lon0  # centering the projection
    alpha = acos(cos(lat) * cos(lon / 2.0))
    sin_alpha = sinc(alpha)
    phi1 = acos(2.0 / pi)
    x = 1 / 2.0 * (lon * cos(phi1) + (2 * cos(lat) * sin(lon / 2.0)) / sin_alpha)
    y = 1 / 2.0 * (lat + sin(lat) / sin_alpha)
    return x, y


def sinc(x):
    if x == 0:
        return 1
    else:
        return sin(x) / x


def lambert_azimuthal_equal_area(lon, lat, lon0=0, lat0=0):
    lon, lat = radians(lon), radians(lat)
    lon0, lat0 = radians(lon0), radians(lat0)
    k = sqrt(2 / (1 + sin(lat0) * sin(lat) + cos(lat0) * cos(lat) * cos(lon - lon0)))
    x = k * cos(lat) * sin(lon - lon0)
    y = k * (cos(lat0) * sin(lat) - sin(lat0) * cos(lat) * cos(lon - lon0))
    return x, y
