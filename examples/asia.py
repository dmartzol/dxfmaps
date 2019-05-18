from dxfmaps.map import Map
from dxfmaps.utils import WORLD_COUNTRIES
from dxfmaps.projections import *


def main():
    map = Map(WORLD_COUNTRIES, continent="asia")
    map.filter_by_area(area_limit=1.0)
    map.info()
    map.simplify(tolerance=0.015)
    map.project(MERCATOR)
    map.translate_to_center()
    map.scale_to_width(3000)
    map.add_labels()
    map.to_png()


if __name__ == "__main__":
    main()
