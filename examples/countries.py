import dxfmaps
from dxfmaps.map import Map
import shapefile

VERBOSE = False


def main():
    sf = shapefile.Reader(dxfmaps.utils.WORLD_COUNTRIES)
    list_of_countries = [
        'norway',
        'spain',
        'france',
        'italy',
        'germany',
        'Denmark',
        'Poland',
        'sweden'
    ]
    map = Map(sf, countries=list_of_countries)
    map.filter_by_area(area_limit=.5)
    projection = 'winkel_tripel'
    map.project(projection)
    map.simplify(tolerance=.015)
    map.translate_to_center()
    map.scale_to_width(200)
    map.add_names()
    map.to_svg(filename='countries-{}.svg'.format(projection))
    # map.to_dxf(filename='countries.dxf')

if __name__ == "__main__":
    main()
