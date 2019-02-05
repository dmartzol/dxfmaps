import shapely
import ezdxf
from shapely.geometry import shape
from dxfmaps.utils import save_svg, scale_adjust
import dxfmaps.projections

class LandNotFound(ValueError):
    pass

class CountryNotInContinentException(Exception):
    pass

class Map(object):
    def __init__(self, sf, continent=None, countries=None):
        self.sf = sf
        self.continent = continent
        self.countries = countries
        self.multipolygon = self.shp_to_multipolygon()
        self.width = None
        self.height = None
        self.units = None
        self.scaling_factor = None
        self.buffered = None
    
    def shp_to_multipolygon(self):
        if self.countries and self.continent:
            raise ValueError("Only one filter is needed.")
        if self.countries:
            geoms = []
            for country in self.countries:
                for shapeRecord in self.sf.shapeRecords():
                    if shapeRecord.record["NAME"].lower() == country.lower():
                        geoms.append(self.build_polygon(shapeRecord))
        elif self.continent:
            geoms = []
            for shapeRecord in self.sf.shapeRecords():
                if shapeRecord.record["CONTINENT"].lower() == self.continent.lower():
                    geoms.append(self.build_polygon(shapeRecord))
            if len(geoms) == 0:
                raise LandNotFound(self.continent)
        else:
            geoms = [self.build_polygon(shapeRecord) for shapeRecord in self.sf.shapeRecords()]
            assert len(geoms)>0, "Countries not found"
        return shapely.geometry.MultiPolygon(geoms)

    def build_polygon(self, shapeRecord):
        """
        If object is a Polygon, returns the object unmodified.
        If object is a Multipolygon, returns the inner polygon with max area
        """
        geom = shape(shapeRecord.shape.__geo_interface__)
        if isinstance(geom, shapely.geometry.polygon.Polygon):
            return geom
        elif isinstance(geom, shapely.geometry.multipolygon.MultiPolygon):
            return self.max_area_polygon(geom)
        else:
            raise Exception('Found non valid geometry')

    def max_area_polygon(self, multipolygon):
        # TODO: Try using max and its index, e.g.
        # index, value = max(list(multipolygon), key=lambda item: item.area)
        p = list(multipolygon)[0]
        for polygon in list(multipolygon):
            if polygon.area > p.area:
                p = polygon
        return p

    def project(self, projection_name):
        """
        Transforms the current GPS coordinates to the chosen projection
        coordinates.
        """
        # print(dir(dxfmaps.projections))
        # projection_names = {"laea", "mercator", "winkel_tripel"}
        if projection_name not in dir(dxfmaps.projections):
            raise ValueError("Wrong projection name")
        new_polygons = []
        for polygon in self.multipolygon.geoms:
            new_coords = []
            for coords in polygon.exterior.coords:
                x, y = getattr(dxfmaps.projections, projection_name)(*coords)
                new_coords.append([x, y])
            new_polygons.append(shapely.geometry.Polygon(new_coords))
        self.multipolygon = shapely.geometry.MultiPolygon(new_polygons)

    def filter_by_area(self, area_thresold):
        """
        Goes through all the polygons inside self.multipolygon and keeps only
        polygons with area greater than area_thresold.
        """
        # TODO: Figure units for area!
        polygons = [polygon for polygon in self.multipolygon.geoms if polygon.area > area_thresold]
        self.multipolygon = shapely.geometry.MultiPolygon(polygons)
        assert len(polygons) > 0, "We removed too many polygons"

    def simplify(self, tolerance = 2000, verbose = False):
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

    def translate_to_center_old(self):
        # Translating the map to the origin
        self.full_map = shapely.geometry.MultiPolygon(self.polygons)
        offset_x = - min(self.full_map.bounds[0], self.full_map.bounds[2])
        offset_y = - min(self.full_map.bounds[1], self.full_map.bounds[3])
        self.full_map = shapely.affinity.translate(self.full_map, xoff=offset_x, yoff=offset_y)

    def translate_to_center(self):
        # Translating the map to the origin
        offset_x = - min(self.multipolygon.bounds[0], self.multipolygon.bounds[2])
        offset_y = - min(self.multipolygon.bounds[1], self.multipolygon.bounds[3])
        self.multipolygon = shapely.affinity.translate(
            self.multipolygon,
            xoff=offset_x,
            yoff=offset_y
        )

    def scale_width(self, width=200, units="mm"):
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

    def scale_height(self, height=100, units="mm"):
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

    def buffer(self):
        interior = self.multipolygon.buffer(0.5, cap_style=2, join_style=1)
        self.buffered = interior.buffer(-1.0, cap_style=2, join_style=1)

    def to_svg(self, filename='out.svg', stroke_width=.2, save_back_buffered=False):
        save_svg(
            self.multipolygon,
            filename=filename,
            width=self.width,
            units=self.units,
            stroke_width=stroke_width
        )
        if save_back_buffered:
            interior = self.multipolygon.buffer(0.5, cap_style=2, join_style=1)
            interior = interior.buffer(-1.0, cap_style=2, join_style=1)
            save_svg(
                interior,
                filename='buffered.svg',
                width=self.width,
                units=self.units,
                stroke_width=stroke_width
            )

    def to_dxf(self, filename='out.dxf'):
        drawing = ezdxf.new('R2000')
        modelspace = drawing.modelspace()
        for polygon in self.multipolygon.geoms:
            vertices = list(polygon.exterior.coords)
            modelspace.add_lwpolyline(vertices)
        # heigth = scale_adjust(3.0)
        drawing.saveas(filename)
