import dxfmaps
import shapefile
import sys
from dxfmaps.projections import mercator

VERBOSE = False


def main():
    sf = shapefile.Reader(dxfmaps.utils.WORLD_COUNTRIES)
    map = dxfmaps.Map(sf, countries=['norway', 'spain'])
    map.filter_by_area(area_thresold=.5)
    map.project('mercator')
    map.simplify(tolerance=.005)
    map.add_names()
    map.translate_to_center()
    map.scale_to_width()
    map.to_svg(filename='norway.svg')
    map.to_dxf(filename='norway.dxf')
    # print(map.multipolygon.centroid)

if __name__ == "__main__":
    main()
