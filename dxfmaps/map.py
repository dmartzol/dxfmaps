import shapely
import ezdxf
from shapely.geometry import shape
from dxfmaps.utils import save_svg, scale_adjust

class LandNotFound(ValueError):
    pass

class CountryNotInContinentException(Exception):
    pass

class Map(object):
    def __init__(self, sf, continent=None, country=None):
        self.sf = sf
        self.continent = continent
        self.country = country
        self.multipolygon = self.shp_to_multipolygon()
        self.width = None
        self.units = None
        self.factor = None
    
    def shp_to_multipolygon(self):
        if self.country and self.continent:
            geoms = []
            for shapeRecord in self.sf.shapeRecords():
                if shapeRecord.record["NAME"].lower() == self.country.lower():
                    if shapeRecord.record["CONTINENT"].lower() != self.continent.lower():
                        error_message = '{} is not in {} according to Shapefile'.format(self.country, self.continent)
                        raise CountryNotInContinentException(error_message)
                    geoms.append(self.build_polygon(shapeRecord))
        elif self.continent:
            geoms = []
            for shapeRecord in self.sf.shapeRecords():
                if shapeRecord.record["CONTINENT"].lower() == self.continent.lower():
                    geoms.append(self.build_polygon(shapeRecord))
            if len(geoms) == 0:
                raise LandNotFound(self.continent)
        elif self.country:
            geoms = []
            for shapeRecord in self.sf.shapeRecords():
                if shapeRecord.record["NAME"].lower() == self.country.lower():
                    geoms.append(self.build_polygon(shapeRecord))
            if len(geoms) == 0:
                raise LandNotFound(self.country)
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
        # TODO: Try using max and its index
        # index, value = max(list(multipolygon), key=lambda item: item.area)
        p = list(multipolygon)[0]
        for polygon in list(multipolygon):
            if polygon.area > p.area:
                p = polygon
        return p
    
    def filter_by_area(self, area_thresold):
        """
        Goes through all the polygons inside self.multipolygon and keeps only polygons with
        area greater than area_thresold.
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
        full_map = shapely.geometry.MultiPolygon(self.polygons)
        offset_x = - min(full_map.bounds[0], full_map.bounds[2])
        offset_y = - min(full_map.bounds[1], full_map.bounds[3])
        full_map = shapely.affinity.translate(full_map, xoff=offset_x, yoff=offset_y)
        for i, polygon in enumerate(full_map.geoms):
            self.polygons[i] = polygon

    def scale(self, width=200, units="mm"):
        # Scaling the map to reduce its width
        self.width = width
        self.units = units
        assert units == "mm", "Other units not implemented yet"
        self.factor = (3.77 * self.width) / max(self.full_map.bounds)
        # print("Scaling factor: {}".format(self.factor))
        # print("Old bounds: {}".format(self.full_map.bounds))
        self.full_map = shapely.affinity.scale(self.full_map, xfact=self.factor, yfact=self.factor, origin=(0, 0))
        # print("New bounds: {}".format(self.full_map.bounds))

    def to_svg(self, filename='out.svg', stroke_width=.5, save_back_buffered=False):
        save_svg(
            self.polygons,
            filename=filename,
            width=self.width,
            units=self.units,
            stroke_width=stroke_width
        )
        if save_back_buffered:
            interior = self.full_map.buffer(0.5, cap_style=2, join_style=1)
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

        for polygon in self.polygons:
            vertices = list(polygon.exterior.coords)
            modelspace.add_lwpolyline(vertices)
        # heigth = scale_adjust(3.0)
        drawing.saveas(filename)
