from dxfmaps.map import Map
from dxfmaps.utils import WORLD_COUNTRIES
from dxfmaps.projections import MERCATOR


def main():
    countries = {"norway"}
    map = Map(WORLD_COUNTRIES, countries_set=countries)
    map.filter_by_area(area_limit=16)
    map.info()
    map.project(MERCATOR)
    map.simplify(tolerance=0.05)
    map.translate_to_center()
    map.scale(705.6870651946915)
    # map.scale_to_width(1000)
    map.add_labels(box=True, n=25)
    map.to_png(white_bg=True)
    map.to_dxf(filename="spain.dxf")


if __name__ == "__main__":
    main()
