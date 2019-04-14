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
        geometries = []
        if self.countries:
            countries = set([x.lower() for x in self.countries])
            for shapeRecord in self.sf.shapeRecords():
                name = shapeRecord.record["NAME"].lower()
                if name in countries:
                    geom = shape(shapeRecord.shape.__geo_interface__)
                    # polygons = utils.get_polygons(geom)
                    geometry = NamedGeometry(geom, name=name)
                    geometries.append(geometry)
        else:
            for shapeRecord in self.sf.shapeRecords():
                name = shapeRecord.record["NAME"].lower()
                geom = shape(shapeRecord.shape.__geo_interface__)
                # polygons = utils.get_polygons(geom)
                geometry = NamedPolygon(geom, name=name)
                geometries.append(geometry)
        if len(geometries) == 0:
            raise ValueError("Countries not found")
        return geometries

    def info(self):
        print('-------- info --------')
        print("{} element(s)".format(len(self.elements)))
        for country in self.elements:
            geo_count = len(country.geometry)
            print("\t{} has {} geometries".format(country.name, geo_count))
            for geo in country.geometry:
                print("\t\t Area {0:.2f}".format(geo.area))

    def filter_by_area(self, area_limit):
        """
        Goes through all the polygons in self.multipolygon and keeps only
        polygons with area greater than area_limit.
        """
        # TODO: Figure units for area!
        new_elements = []
        for element in self.elements:
            new_elements.append(element.filter_by_area(area_limit))
        self.elements = new_elements
        if len(self.elements) < 1:
            raise ValueError("We removed too many polygons")

    def project_old(self, projection_name):
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
        new_dict = {}
        for name, polygons in self.countries_by_name.items():
            new_polygons = []
            for polygon in polygons:
                new_coords = []
                for coords in polygon.exterior.coords:
                    x, y = getattr(projections, projection_name)(*coords)
                    new_coords.append([x, y])
                new_polygons.append(shapely.geometry.Polygon(new_coords))
            new_dict[name] = new_polygons
        self.countries_by_name = new_dict

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

    def add_names(self):  # TODO: Rename?
        """
        Processes the name for every country/province and includes it into
        self.multipolygon as a polygon.
        """
        new_polygons = []
        for polygon, name in zip(self.multipolygon, self.countries):
            label = text.label(polygon, name)
            new_polygons.extend([polygon, *label])
        self.multipolygon = shapely.geometry.MultiPolygon(new_polygons)

    def buffer(self, grow=0.5, shrink=-1.0):  # TODO: Rename
        """Applies a growing buffer and a shrinking to every polygon
        """
        interior = self.multipolygon.buffer(grow, cap_style=2, join_style=1)
        self.multipolygon = interior.buffer(shrink, cap_style=2, join_style=1)
