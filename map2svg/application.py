# from map2svg.utils import *
from map2svg.map import Map
import shapefile

VERBOSE = False

# TODO - Change projections
# TODO - Implement parsing options from CLI
# TODO - Implement printing county names

US_STATES = "shapefiles/cb_2017_us_state_500k/cb_2017_us_state_500k.shp"
WORLD_COUNTRIES = "shapefiles/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"
WORLD_COUNTRIES2 = "shapefiles/ne_50m_admin_0_countries/ne_50m_admin_0_countries.shp"
STATES_PROVINCES = "shapefiles/ne_10m_admin_1_states_provinces/ne_10m_admin_1_states_provinces.shp"

def main():
    sf = shapefile.Reader(WORLD_COUNTRIES)
    # item_info(sf, 3)
    # print("Number of records: {}".format(sf.numRecords))
    map = Map(sf, continent='north america')
    map.filter_by_area(area_thresold = .5)
    map.simplify(tolerance=.05)
    map.translate_to_center()
    map.scale()
    map.to_svg()
