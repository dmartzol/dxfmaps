from dxfmaps.map import Map
from dxfmaps.utils import WORLD_COUNTRIES
from dxfmaps.projections import *


def main():
    countries = {'Sweden'}
    map = Map(WORLD_COUNTRIES, countries_set=countries)
    map.filter_by_area(area_limit=16)
    map.info()
    map.project(MERCATOR)
    map.simplify(tolerance=.04)
    map.translate_to_center()
    map.scale_to_width(1000)
    # map.add_labels()
    map.to_png(white_bg=True)
    print(map.countries[0].contours[0].wkt)
    print(map.width)
    # map.to_svg(filename='spain.svg')


if __name__ == "__main__":
    main()
