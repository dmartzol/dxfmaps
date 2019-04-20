from dxfmaps.map import Map
from dxfmaps.utils import WORLD_COUNTRIES
from dxfmaps.projections import *


def main():
    map = Map(WORLD_COUNTRIES, continent="europe")
    map.filter_by_area(area_limit=1.0)
    map.simplify(tolerance=.015)
    map.project(MERCATOR)
    map.translate_to_center()
    map.scale_to_width(5000)
    map.add_labels()
    map.to_png(stroke_width=2.0)
    map.to_svg()
    map.to_dxf()


if __name__ == "__main__":
    main()
