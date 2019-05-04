from dxfmaps.map import Map
from dxfmaps.utils import WORLD_COUNTRIES
from dxfmaps.projections import *

TOLERANCE = 0.015
AREA_LIMIT = 2.0


def main():
    map = Map(WORLD_COUNTRIES, continent="europe")
    map.filter_by_area(area_limit=AREA_LIMIT)
    map.simplify(tolerance=TOLERANCE)
    map.info()
    map.project(MERCATOR)
    map.translate_to_center()
    map.scale_to_width(2000)
    scaling_factor = map.scaling_factor
    map.to_dxf(filename='europe.dxf')
    map.to_png(filename='europe.png', white_bg=True)

    countries = map.countries_set
    countries = {'Spain', 'Portugal'}
    for country in countries:
        country_set = set([country])
        map_by_pieces = Map(WORLD_COUNTRIES, countries_set=country_set)
        map_by_pieces.filter_by_area(area_limit=2.0)
        map_by_pieces.simplify(tolerance=.015)
        map_by_pieces.project(MERCATOR)
        map_by_pieces.translate_to_center()
        map_by_pieces.scale(scaling_factor)
        map_by_pieces.add_labels(box=True, n=45)
        map_by_pieces.to_svg(filename=country + '.svg')
        map_by_pieces.to_dxf(filename=country + '.dxf')


if __name__ == "__main__":
    main()
