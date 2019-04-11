import dxfmaps
from dxfmaps.projections import mercator
from dxfmaps.map import Map
import shapefile


def main():
    sf = shapefile.Reader(dxfmaps.utils.WORLD_COUNTRIES)
    countries = ['france']
    map = Map(sf, countries=countries)
    map.filter_by_area(area_limit=.5)
    map.project('LambertAzimuthalEqualArea')
    map.simplify(tolerance=.0002)
    map.translate_to_center()
    map.scale_to_width(200)
    map.add_names()
    map.to_svg(filename='spain.svg')

if __name__ == "__main__":
    main()
