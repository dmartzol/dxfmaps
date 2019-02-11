import dxfmaps
import shapefile
import sys
from dxfmaps.projections import mercator

VERBOSE = False


def main():
    sf = shapefile.Reader(dxfmaps.utils.WORLD_COUNTRIES)
    map = dxfmaps.Map(sf, continent="europe")
    map.filter_by_area(area_thresold=.5)
    map.project('mercator')
    map.simplify(tolerance=.05)
    map.translate_to_center()
    map.scale_to_width()
    map.to_svg(filename='europe.svg')
    map.to_dxf(filename='europe.dxf')

if __name__ == "__main__":
    main()