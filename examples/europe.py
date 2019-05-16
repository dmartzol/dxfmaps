from dxfmaps.map import Map
from dxfmaps.utils import WORLD_COUNTRIES
from dxfmaps.projections import MERCATOR

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
    countries = {
            'slovakia',
            'spain',
            'norway',
            'italy',
            'slovenia',
            'san marino',
            'andorra',
            'croatia',
            'moldova',
            'hungary',
            'denmark',
            'latvia',
            'ireland',
            'serbia',
            'åland',
            'malta',
            'bosnia and herz.',
            'austria',
            'czechia',
            'switzerland',
            'portugal',
            'lithuania',
            'poland',
            'sweden',
            'liechtenstein',
            'russia',
            'france',
            'estonia',
            'germany',
            'greece',
            'jersey',
            'kosovo',
            'belgium',
            'romania',
            'isle of man',
            'united kingdom',
            'montenegro',
            'netherlands',
            'luxembourg',
            'iceland',
            'ukraine',
            'belarus',
            'macedonia',
            'faeroe is.',
            'guernsey',
            'bulgaria',
            'gibraltar',
            'albania',
            'vatican',
            'monaco',
            'finland'
    }

    for country in countries:
        country_set = set([country])
        map_by_pieces = Map(WORLD_COUNTRIES, countries_set=country_set)
        map_by_pieces.filter_by_area(area_limit=AREA_LIMIT)
        map_by_pieces.simplify(tolerance=TOLERANCE)
        map_by_pieces.project(MERCATOR)
        map_by_pieces.translate_to_center()
        map_by_pieces.scale(scaling_factor)
        map_by_pieces.add_labels(n=35)
        map_by_pieces.to_svg(filename=country + '.svg')
        map_by_pieces.to_dxf(filename=country + '.dxf')
        break


if __name__ == "__main__":
    main()
