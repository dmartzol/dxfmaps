import dxfmaps
import shapefile
from dxfmaps.projections import mercator

VERBOSE = False


def main():
    sf = shapefile.Reader(dxfmaps.utils.WORLD_COUNTRIES)
    countries = ['France']
    map = dxfmaps.Map(sf, countries=countries)
    map.filter_by_area(area_limit=.5)
    map.project('LambertAzimuthalEqualArea')
    map.simplify(tolerance=.0002)
    map.translate_to_center()
    map.scale_to_width()
    map.add_names()
    map.to_svg(filename='france.svg')
    map.to_dxf(filename='france.dxf')
    map.buffer()
    map.to_svg(filename='france0.svg')
    map.to_dxf(filename='france0.dxf')

if __name__ == "__main__":
    main()
