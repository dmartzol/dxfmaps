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
        self.polygons = self.shapefile2polygons()
        self.full_map = None
        self.size = None
        self.units = None
        self.factor = None
    
    def shapefile2polygons(self):
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
        return geoms
    
    def build_polygon(self, shapeRecord):
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
        # TODO: Figure units for area!
        self.polygons = [polygon for polygon in self.polygons if polygon.area > area_thresold]
        assert len(self.polygons) > 0, "We removed too many polygons"
    
    def full_map(self):
        return shapely.geometry.MultiPolygon(polygons)
    
    def simplify(self, tolerance = 2000, verbose = False):
        # TODO: calculate adequate tolerance
        for i, polygon in enumerate(self.polygons):
            nodes_before = len(list(polygon.exterior.coords))
            self.polygons[i] = self.polygons[i].simplify(tolerance=tolerance)
            if verbose:
                nodes = len(list(polygon.exterior.coords))
                print("Polygon nodes reduced by {:.1f}%, from {} to {}".format(
                    100*(nodes_before-nodes)/float(nodes_before),
                    nodes_before,
                    nodes
                    )
                )

    def translate_to_center(self):
        # Translating the map to the origin
        # TODO - Choose a better name
        self.full_map = shapely.geometry.MultiPolygon(self.polygons)
        offset_x = - min(self.full_map.bounds[0], self.full_map.bounds[2])
        offset_y = - min(self.full_map.bounds[1], self.full_map.bounds[3])
        self.full_map = shapely.affinity.translate(self.full_map, xoff=offset_x, yoff=offset_y)

    def scale(self, size=200, units="mm"):
        # Scaling the map to reduce its size
        self.size = size
        self.units = units
        self.factor = (3.77 * self.size) / max(self.full_map.bounds)
        # print("")
        # print("Scaling factor: {}".format(self.factor))
        # print("Old bounds: {}".format(self.full_map.bounds))
        self.full_map = shapely.affinity.scale(self.full_map, xfact=self.factor, yfact=self.factor, origin=(0, 0))
        # print("New bounds: {}".format(self.full_map.bounds))

    def to_svg(self, filename='out.svg', stroke_width=.5, save_back_buffered=False):
        save_svg(
            self.full_map,
            filename=filename,
            size=self.size,
            units=self.units,
            stroke_width=stroke_width
        )
        if save_back_buffered:
            interior = self.full_map.buffer(0.5, cap_style=2, join_style=1)
            interior = interior.buffer(-1.0, cap_style=2, join_style=1)
            save_svg(
                interior,
                filename='buffered.svg',
                size=self.size,
                units=self.units,
                stroke_width=stroke_width
            )
    def to_dxf(self, filename='out.dxf'):
        drawing = ezdxf.new('R2000')
        modelspace = drawing.modelspace()
        drawing.layers.new('BOUNDARIES_LAYER', dxfattribs={'color': 255})
        heigth = scale_adjust(3.0)
        modelspace.add_text('Test', dxfattribs={'layer': 'TEXTLAYER', 'height': heigth, 'style': 'standard'}).set_pos((0, 0), align='CENTER')
# 0.001 + 0.734 x

        # modelspace.add_line((0, 0), (10, 0), dxfattribs={'color': 7})
        # drawing.layers.new('TEXTLAYER', dxfattribs={'color': 2})
        # modelspace.add_text('Test', dxfattribs={'layer': 'TEXTLAYER'}).set_pos((0, 0.2), align='CENTER')
        drawing.saveas(filename)
