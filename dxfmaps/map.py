import shapely
import ezdxf
from shapely.geometry import shape
from dxfmaps import utils
from dxfmaps import projections
from dxfmaps import fonts
from dxfmaps import text
from .geometricfigure import GeometricFigure


class LandNotFound(ValueError):
    pass


class Map(GeometricFigure):
    def __init__(self, sf, continent=None, countries=None):
        self.sf = sf
        self.continent = continent
        self.countries = countries
        self.scaling_factor = None
        return super().__init__(self.shp_to_multipolygon())

    def shp_to_multipolygon(self):
        if self.countries and self.continent:
            raise ValueError("Only one filter is needed.")
        if self.countries:
            geoms = []
            for country in self.countries:
                for shapeRecord in self.sf.shapeRecords():
                    if shapeRecord.record["NAME"].lower() == country.lower():
                        geom = shape(shapeRecord.shape.__geo_interface__)
                        geoms.append(utils.multipolygon_to_polygon(geom))
        elif self.continent:
            geoms = []
            for shapeRecord in self.sf.shapeRecords():
                cont_in_records = shapeRecord.record["CONTINENT"].lower()
                if cont_in_records == self.continent.lower():
                    geoms.append(self.build_polygon(shapeRecord))
            if len(geoms) == 0:
                raise LandNotFound(self.continent)
        else:
            geoms = [self.build_polygon(x) for x in self.sf.shapeRecords()]
            assert len(geoms) > 0, "Countries not found"
        return shapely.geometry.MultiPolygon(geoms)

    def project(self, projection_name):
        """
        Transforms the current GPS coordinates to the chosen projection
        coordinates.
        Available projections:
            - laea
            - mercator
            - winkel_tripel
        """
        if projection_name not in dir(projections):
            raise ValueError("Wrong projection name")
        new_polygons = []
        for polygon in self.multipolygon.geoms:
            new_coords = []
            for coords in polygon.exterior.coords:
                x, y = getattr(projections, projection_name)(*coords)
                new_coords.append([x, y])
            new_polygons.append(shapely.geometry.Polygon(new_coords))
        self.multipolygon = shapely.geometry.MultiPolygon(new_polygons)

    def filter_by_area(self, area_limit):
        """
        Goes through all the polygons in self.multipolygon and keeps only
        polygons with area greater than area_limit.
        """
        # TODO: Figure units for area!
        polygons = [x for x in self.multipolygon.geoms if x.area > area_limit]
        self.multipolygon = shapely.geometry.MultiPolygon(polygons)
        assert len(polygons) > 0, "We removed too many polygons"

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
