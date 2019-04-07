# from dxfmaps.utils import *
# from dxfmaps import Map
import dxfmaps
import shapefile

VERBOSE = False

# TODO - Implement DXF output
# TODO - Change projections
# TODO - Implement parsing options from CLI
# TODO - Implement printing country names

US_STATES = "shapefiles/cb_2017_us_state_500k/cb_2017_us_state_500k.shp"
WORLD_COUNTRIES = "shapefiles/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"
WORLD_COUNTRIES2 = "shapefiles/ne_50m_admin_0_countries/ne_50m_admin_0_countries.shp"
STATES_PROVINCES = "shapefiles/ne_10m_admin_1_states_provinces/ne_10m_admin_1_states_provinces.shp"


def main():
    sf = shapefile.Reader(WORLD_COUNTRIES)
    map = dxfmaps.Map(sf, continent='europe')
    # map = Map(sf, continent='europe')
    # map.filter_by_area(area_thresold = .5)
    # map.simplify(tolerance=.05)
    # map.translate_to_center()
    # map.scale()
    # map.to_svg()
