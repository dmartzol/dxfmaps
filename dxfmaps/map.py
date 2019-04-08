import shapely
import ezdxf
from shapely.geometry import shape
from dxfmaps import utils
from dxfmaps import projections
from dxfmaps import fonts
from dxfmaps import text


class LandNotFound(ValueError):
    pass


class CountryNotInContinentException(Exception):
    pass


class Map:
    def __init__(self, sf, continent=None, countries=None):
        self.sf = sf
        self.continent = continent
        self.countries = countries
        self.multipolygon = self.shp_to_multipolygon()
        self.width = None
        self.height = None
        self.units = None
        self.scaling_factor = None

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
        -laea
        -mercator
        -winkel_tripel
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

    def simplify(self, tolerance=2000, verbose=False):
        """
        Removes nodes from the path of every polygon according to tolerance
        """
        polygons = [polygon for polygon in self.multipolygon.geoms]
        for i, polygon in enumerate(polygons):
            nodes_before = len(list(polygon.exterior.coords))
            polygons[i] = polygons[i].simplify(tolerance=tolerance)
            if verbose:
                nodes = len(list(polygon.exterior.coords))
                print("Polygon nodes reduced by {:.1f}%, from {} to {}".format(
                    100*(nodes_before-nodes)/float(nodes_before),
                    nodes_before,
                    nodes
                    )
                )
        self.multipolygon = shapely.geometry.MultiPolygon(polygons)

    def translate_to_center(self):
        """
        Translates the map to the origin (0, 0)
        """
        minx, miny, maxx, maxy = self.multipolygon.bounds
        x_offset = - min(minx, maxx)
        y_offset = - min(miny, maxy)
        self.multipolygon = shapely.affinity.translate(
            self.multipolygon,
            xoff=x_offset,
            yoff=y_offset
        )

    def scale_to_width(self, width=200, units="mm"):
        """
        Scales the map to a specific width
        """
        self.width = width
        self.units = units
        current_width = self.multipolygon.bounds[2]
        assert units == "mm", "Other units not implemented yet(only mm)"
        self.scaling_factor = self.width / current_width
        self.multipolygon = shapely.affinity.scale(
            self.multipolygon,
            xfact=self.scaling_factor,
            yfact=self.scaling_factor,
            origin=(0, 0)
        )

    def scale_to_height(self, height=100, units="mm"):
        """
        Scales the map to a specific heigh
        """
        self.height = height
        self.units = units
        current_height = self.multipolygon.bounds[3]
        assert units == "mm", "Other units not implemented yet(only mm)"
        self.scaling_factor = self.height / current_height
        self.multipolygon = shapely.affinity.scale(
            self.multipolygon,
            xfact=self.scaling_factor,
            yfact=self.scaling_factor,
            origin=(0, 0)
        )

    def buffer(self, grow=0.5, shrink=-1.0):
        interior = self.multipolygon.buffer(grow, cap_style=2, join_style=1)
        self.multipolygon = interior.buffer(shrink, cap_style=2, join_style=1)

    def add_names(self):
        """
        Processes the name for every country/province and includes it into
        self.multipolygon as a polygon.
        """
        new_polygons = []
        for polygon, name in zip(self.multipolygon, self.countries):
            label = text.label(polygon, name)
            new_polygons.extend([polygon, *label])
        self.multipolygon = shapely.geometry.MultiPolygon(new_polygons)

    def to_svg(self, filename='out.svg', stroke_width=.2, back_buffered=False):
        utils.save_svg(
            self.multipolygon,
            filename=filename,
            width=self.width,
            units=self.units,
            stroke_width=stroke_width
        )
        if back_buffered:
            interior = self.multipolygon.buffer(0.5, cap_style=2, join_style=1)
            interior = interior.buffer(-1.0, cap_style=2, join_style=1)
            utils.save_svg(
                interior,
                filename='buffered.svg',
                width=self.width,
                units=self.units,
                stroke_width=stroke_width
            )

    def to_dxf(self, filename='out.dxf'):
        drawing = ezdxf.new('R2000')
        modelspace = drawing.modelspace()
        if isinstance(self.multipolygon, shapely.geometry.MultiPolygon):
            for polygon in self.multipolygon.geoms:
                vertices = list(polygon.exterior.coords)
                modelspace.add_lwpolyline(vertices)
        elif isinstance(self.multipolygon, shapely.geometry.Polygon):
            polygon = self.multipolygon
            vertices = list(polygon.exterior.coords)
            modelspace.add_lwpolyline(vertices)
        # heigth = utils.scale_adjust(3.0)
        drawing.saveas(filename)
