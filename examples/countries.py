from dxfmaps.map import Map
from dxfmaps.utils import WORLD_COUNTRIES
from dxfmaps.projections import *


def main():
    countries = {
        "norway",
        "spain",
        "portugal",
        "france",
        "italy",
        "germany",
        "Denmark",
        "Poland",
        "sweden",
        "Australia",
        "russia",
        "China",
    }
    map = Map(WORLD_COUNTRIES, countries_set=countries)
    map.filter_by_area(area_limit=4.0)
    map.info()
    map.project(MERCATOR)
    map.simplify(tolerance=0.001)
    map.translate_to_center()
    map.scale_to_width(3000)
    map.add_labels()
    map.to_png()
    # map.to_svg(filename='countries-{}.svg'.format(projection))
    # map.to_dxf(filename='countries.dxf')


if __name__ == "__main__":
    main()
