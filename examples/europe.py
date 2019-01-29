import dxfmaps
import shapefile
import sys

VERBOSE = False

WORLD_COUNTRIES = "../shapefiles/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"
WORLD_PROVINCES = '/shapefiles/ne_10m_admin_1_states_provinces/ne_10m_admin_1_states_provinces.shp'

def main():
    sf = shapefile.Reader(WORLD_COUNTRIES)
    map = dxfmaps.Map(sf, continent='europe')
    map.filter_by_area(area_thresold = .5)
    map.simplify(tolerance=.05)
    map.translate_to_center()
    map.scale(width=300, units='mm')
    map.to_svg(filename='europe.svg')
    map.to_dxf()

if __name__ == "__main__":
    main()