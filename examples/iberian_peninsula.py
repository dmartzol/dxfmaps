from dxfmaps.map import Map
from dxfmaps.utils import WORLD_COUNTRIES
from dxfmaps.projections import *


def main():
    countries = {
        'spain',
        'portugal'
    }
    map = Map(WORLD_COUNTRIES, countries_set=countries, country_field='NAME')
    map.filter_by_area(area_limit=0.30)
    map.project(MERCATOR)
    map.simplify()
    map.translate_to_center()
    map.scale_to_width(1000)
    map.add_labels()
    map.to_png()
    map.to_svg(filename='iberian.svg')
    map.to_dxf(filename='iberian.dxf')
    # map.buffer()
    # map.to_svg(filename='iberian0.svg')
    # map.to_dxf(filename='iberian0.dxf')


if __name__ == "__main__":
    main()
