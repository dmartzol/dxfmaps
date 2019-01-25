# from dxfmaps.utils import *
from dxfmaps import Map
import dxfmaps
import shapefile
import sys

VERBOSE = False

# TODO - Implement DXF output
# TODO - Change projections
# TODO - Implement printing country names
# TODO - Change name of output buffered file

WORLD_COUNTRIES = "../shapefiles/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"

def main():
    sf = shapefile.Reader(sys.argv[1])
    map = Map(sf, continent='europe')
    map.filter_by_area(area_thresold = .5)
    map.simplify(tolerance=.05)
    map.translate_to_center()
    map.scale()
    map.to_svg(filename='europe.svg')

if __name__ == "__main__":
    main()