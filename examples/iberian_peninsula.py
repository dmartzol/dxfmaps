import dxfmaps
import shapefile
from dxfmaps.projections import mercator
from dxfmaps.map import Map

VERBOSE = False


def main():
    sf = shapefile.Reader(dxfmaps.utils.WORLD_COUNTRIES)
    countries = ['spain', 'portugal']
    map = Map(sf, countries=countries)
    map.filter_by_area(area_limit=.5)
    map.project('LambertAzimuthalEqualArea')
    map.simplify(tolerance=.0002)
    map.translate_to_center()
    map.scale_to_width(200)
    map.add_names()
    map.to_svg(filename='iberian.svg')
    map.to_dxf(filename='iberian.dxf')
    map.buffer()
    map.to_svg(filename='iberian0.svg')
    map.to_dxf(filename='iberian0.dxf')

if __name__ == "__main__":
    main()
