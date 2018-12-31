from map2svg import names
from map2svg.utils import *
from map2svg.map import Map
import shapely
import sys
import shapefile

# TODO - Change projections
# TODO - Print single selected country

US_STATES = "shapefiles/cb_2017_us_state_500k/cb_2017_us_state_500k.shp"
WORLD_COUNTRIES = "shapefiles/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"
WORLD_COUNTRIES2 = "shapefiles/ne_50m_admin_0_countries/ne_50m_admin_0_countries.shp"
STATES_PROVINCES = "shapefiles/ne_10m_admin_1_states_provinces/ne_10m_admin_1_states_provinces.shp"

def main():
    sf = shapefile.Reader(WORLD_COUNTRIES)
    # item_info(sf, 9)
    # countries_by_continent(sf, "America")
    # list_of_countries(sf)
    # list_of_continents(sf)
    # print("Number of records: {}".format(sf.numRecords))
    map = Map(sf, continent='Asia')



    polygons = shapefile2polygons(sf, continent='Asia')
    records = sf.records()

    print("Polygons before filtering by area: {}".format(len(polygons)))
    polygons = filter_by_area(polygons, area_thresold = .5)
    assert (len(polygons) > 0), "Filtered too many polygons"
    print("Polygons after filtering by area: {}".format(len(polygons)))
    
    simplify(polygons, tolerance = .3)

    # Translating the map to the origin
    full_map = shapely.geometry.MultiPolygon(polygons)
    offset_x = - min(full_map.bounds[0], full_map.bounds[2])
    offset_y = - min(full_map.bounds[1], full_map.bounds[3])
    full_map = shapely.affinity.translate(full_map, xoff=offset_x, yoff=offset_y)

    # Scaling the map to reduce its size
    # size = 200
    # units = "mm"
    # factor = (3.77 * size) / max(full_map.bounds)
    # print("")
    # print("Scaling factor: {}".format(factor))
    # print("Old bounds: {}".format(full_map.bounds))
    # full_map = shapely.affinity.scale(full_map, xfact=factor, yfact=factor, origin=(0, 0))
    # print("New bounds: {}".format(full_map.bounds))

    # save_svg(full_map, size=size, units=units, stroke_width=.5)
    # interior = full_map.buffer(0.5, cap_style=2, join_style=1)
    # interior = interior.buffer(-1.0, cap_style=2, join_style=1)
    # save_svg(interior, filename='out_buffered.svg', size=size, units=units, stroke_width=.5)
