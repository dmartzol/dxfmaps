import dxfmaps
from dxfmaps.map import Map
from dxfmaps.projections import mercator
import shapefile

VERBOSE = False


def main():
    sf = shapefile.Reader(dxfmaps.utils.WORLD_COUNTRIES)
    map = Map(sf, continent="asia")
    # map.filter_by_area(area_limit=1.5)
    # map.project('mercator')
    # map.simplify(tolerance=.015)
    # map.translate_to_center()
    map.scale_to_width(1000)
    # map.add_names()
    # map.to_svg(filename='asia.svg')
    map.to_png()

if __name__ == "__main__":
    main()
