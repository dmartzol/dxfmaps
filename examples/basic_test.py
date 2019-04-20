from dxfmaps.map import Map
from dxfmaps.utils import WORLD_COUNTRIES
from dxfmaps.projections import *


def main():
    countries = {'China'}
    map = Map(WORLD_COUNTRIES, countries_set=countries)
    map.filter_by_area(area_limit=.1)
    map.info()
    map.project(MERCATOR)
    map.simplify(tolerance=.0002)
    map.translate_to_center()
    map.scale_to_width(1000)
    map.add_labels()
    map.to_png()
    # map.to_svg(filename='spain.svg')


if __name__ == "__main__":
    main()
