import dxfmaps
import shapefile
import sys
from dxfmaps.projections import mercator

VERBOSE = False


def main():
    sf = shapefile.Reader(dxfmaps.utils.WORLD_COUNTRIES)
    list_of_countries = [
        'norway',
        'spain',
        'france',
        'italy',
        'germany',
        'Denmark',
        'Poland',
        'sweden'
    ]
    map = dxfmaps.Map(sf, countries=list_of_countries)
    map.filter_by_area(area_thresold=.5)
    map.project('mercator')
    map.simplify(tolerance=.015)
    map.translate_to_center()
    map.scale_to_width()
    map.add_names()
    map.to_svg(filename='countries.svg')
    map.to_dxf(filename='countries.dxf')
    # print(map.multipolygon.centroid)

if __name__ == "__main__":
    main()
