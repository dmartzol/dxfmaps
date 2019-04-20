import shapely
import ezdxf
from shapely.geometry import shape
from dxfmaps import utils
from dxfmaps import projections
from dxfmaps import fonts
from dxfmaps import text
from .geometricfigure import GeometricFigure
from .namedgeometry import NamedGeometry


class Map(GeometricFigure):
    def __init__(self, sf, continent=None, countries=None):
        self.sf = sf
        if countries and continent:
            raise ValueError("Only one filter is needed.")
        elif continent:
            self.countries = self._get_countries_from(continent)
        else:
            self.countries = countries
        self.scaling_factor = None
        return super().__init__(self._shp_to_namedpolygon())

    def _get_countries_from(self, continent) -> set():
        countries = set()
        for shapeRecord in self.sf.shapeRecords():
            continent_in_record = shapeRecord.record["CONTINENT"].lower()
            if continent_in_record == continent.lower():
                country = shapeRecord.record["NAME"].lower()
                countries.add(country)
        if len(countries) == 0:
            raise ValueError("No countries found for that continent")
        return countries

    def _shp_to_namedpolygon(self):
        named_polygons = []
        if self.countries:
            countries = set([x.lower() for x in self.countries])
            for shapeRecord in self.sf.shapeRecords():
                name = shapeRecord.record["NAME"].lower()
                if name in countries:
                    geom = shape(shapeRecord.shape.__geo_interface__)
                    named_pol = NamedGeometry(geom, name=name)
                    print(named_pol.name)
                    named_polygons.append(named_pol)
        else:
            # Getting all countries in the world!
            for shapeRecord in self.sf.shapeRecords():
                name = shapeRecord.record["NAME"].lower()
                geom = shape(shapeRecord.shape.__geo_interface__)
                named_pol = NamedGeometry(geom, name=name)
                named_polygons.append(named_pol)
        if len(named_polygons) == 0:
            raise ValueError("Countries not found")
        return named_polygons

    def info(self):
        print('-------- info --------')
        print("{} countries".format(len(self.elements)))
        for country in self.elements:
            print(type(country))
        for country in self.elements:
            print(country.name)
            polygons = country.as_polygons()
            geo_count = len(polygons)
            print("\t{} has {} geometries".format(country.name, geo_count))
            for p in polygons:
                print("\t\t Area {0:.2f}".format(p.area))

    def filter_by_area(self, area_limit):
        """
        Goes through all the polygons in self.multipolygon and keeps only
        polygons with area greater than area_limit.
        """
        # TODO: Figure units for area!
        new_elements = []
        for element in self.elements:
            filtered = element.filter_by_area(area_limit)
            if filtered is not None:
                new_elements.append(filtered)
        self.elements = new_elements
        if len(self.elements) < 1:
            raise ValueError("We removed too many polygons")

    def project(self, projection_name):
        """
        Transforms the current GPS coordinates to the chosen projection
        coordinates.
        Available projections:
            - LambertAzimuthalEqualArea
            - mercator
            - winkel_tripel
        """
        if projection_name not in dir(projections):
            raise ValueError("Wrong projection name")
        new_elements = []
        for country in self.elements:
            new_elements.append(country.project(projection_name))
        self.elements = new_elements

    def add_names(self, box=False):  # TODO: Rename?
        """
        Processes the name for every country/province and includes it into
        self.multipolygon as a polygon.
        """
        new_elements = []
        for country in self.elements:
            label = text.label(country.as_polygons(), country.name, box=box)
            new_elements.append(country)
            new_elements.append(label)
        self.elements = new_elements

    def buffer(self, grow=0.5, shrink=-1.0):  # TODO: Rename
        """Applies a growing buffer and a shrinking to every polygon
        """
        interior = self.multipolygon.buffer(grow, cap_style=2, join_style=1)
        self.multipolygon = interior.buffer(shrink, cap_style=2, join_style=1)
