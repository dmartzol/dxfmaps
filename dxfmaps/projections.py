import math

EARTH_RADIUS = 6378137

def azimuthal_equidistant_proj(self, lon, lat):
    """
    Transforms coordinates from GPS(WSG84) to Azimuthal (WIP)
    """
    x = lat * math.sin(lon)
    y = - lat * math.cos(lon)
    return x, y

def mercator(lon, lat):
    """
    Transforms coordinates from GPS(WSG84) to Mercator
    """
    x = EARTH_RADIUS * math.radians(lon)
    scale = x/lon
    A = math.pi/4.0 + lat * (math.pi/180.0)/2.0
    y = scale * 180.0/math.pi * math.log(math.tan(A))
    return (x, y)
