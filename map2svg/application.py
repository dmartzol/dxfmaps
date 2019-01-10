from map2svg.utils import *
from map2svg.map import Map
import shapefile

VERBOSE = False

# TODO - Change projections
# TODO - Print single selected country
# TODO - Implement parsing options from CLI

US_STATES = "shapefiles/cb_2017_us_state_500k/cb_2017_us_state_500k.shp"
WORLD_COUNTRIES = "shapefiles/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"
WORLD_COUNTRIES2 = "shapefiles/ne_50m_admin_0_countries/ne_50m_admin_0_countries.shp"
STATES_PROVINCES = "shapefiles/ne_10m_admin_1_states_provinces/ne_10m_admin_1_states_provinces.shp"

def main():
    sf = shapefile.Reader(WORLD_COUNTRIES)
    item_info(sf, 9)
    # countries_by_continent(sf, "America")
    # list_of_countries(sf)
    # list_of_continents(sf)
    # print("Number of records: {}".format(sf.numRecords))
    map = Map(sf, continent='Asia')
    map.filter_by_area(area_thresold = .5)

    if VERBOSE:
        print("Polygons before filtering by area: {}".format(len(map.polygons)))
        # polygons = filter_by_area(polygons, area_thresold = .5)
        assert (len(map.polygons) > 0), "Filtered too many polygons"
        print("Polygons after filtering by area: {}".format(len(map.polygons)))
    
    map.simplify(tolerance=.1)
    map.translate_to_center()
    map.scale()
    map.to_svg()
