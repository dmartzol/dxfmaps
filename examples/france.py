import dxfmaps
from dxfmaps.projections import mercator
from dxfmaps.map import Map
import shapefile


VERBOSE = False


def main():
    sf = shapefile.Reader(dxfmaps.utils.WORLD_COUNTRIES)
    countries = ['germany', 'france', 'spain', 'portugal']
    map = Map(sf, countries=countries)
    map.filter_by_area(area_limit=1.0)
    map.project('LambertAzimuthalEqualArea')
    # map.info()
    map.translate_to_center()
    map.scale_to_width(1000)
    map.simplify(tolerance=1.0)
    # map.add_names()
    # map.to_svg(filename='france.svg')
    map.to_png(filename='france1.png', stroke_width=.50)
    # map.to_dxf(filename='france.dxf')
    # map.buffer()
    # map.to_svg(filename='france0.svg')
    # map.to_dxf(filename='france0.dxf')

if __name__ == "__main__":
    main()
