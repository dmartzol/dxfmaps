import shapely
import shapely.wkt
from shapely import affinity
from shapely import geometry
from dxfmaps import utils
from .fonts import *
import cairocffi as cairo


class Text:
    def __init__(self, string, font=VERA, relative_spacing=0.1):
        self.string = string
        self.font = font
        self.spacing = relative_spacing * self.em_width
        self.polygons = self._build_polygons()

    @property
    def as_multipolygon(self):
        return geometry.MultiPolygon(self.polygons)

    @property
    def centroid(self):
        return self.as_multipolygon.centroid

    @property
    def width(self):
        minx, _, maxx, _ = self.bounds
        return maxx - minx

    @property
    def height(self):
        _, miny, _, maxy = self.bounds
        return maxy - miny

    @property
    def bounds(self):
        return self.as_multipolygon.bounds

    @property
    def em_width(self):
        m = shapely.wkt.loads(self.font['M'])
        minx, miny, maxx, maxy = m.bounds
        em_width = maxx - minx
        return em_width

    def _build_polygons(self):
        string = self.string
        font = self.font
        geoms = []
        right_bounds = []
        for char in string:
            if char not in font:
                msg = "Character {} not in font.({})".format(ord(char), string)
                if right_bounds:
                    right_bounds.append(right_bounds[-1])
                print(msg)
                continue
            geom = shapely.wkt.loads(font[char])
            minx, _, _, _ = geom.bounds
            if right_bounds:
                x_offset = right_bounds[-1] - minx + self.spacing
                geom = affinity.translate(geom, xoff=x_offset)
            _, _, maxx, _ = geom.bounds
            right_bounds.append(maxx)
            geoms.extend(utils.get_polygons(geom))
        return geoms

    def rotate(self, angle):
        multipolygon = geometry.MultiPolygon(self.polygons)
        multipolygon = affinity.rotate(multipolygon, angle)
        self.polygons = [x for x in multipolygon]

    def scale(self, factor):
        """
        Scales the geometries to a specific width
        """
        multipolygon = geometry.MultiPolygon(self.polygons)
        multipolygon = affinity.scale(
            multipolygon,
            xfact=factor,
            yfact=factor
        )
        self.polygons = [x for x in multipolygon]

    def translate_to(self, target):
        """
        Translates all the geometries to the origin (0, 0)
        """
        text_center = self.centroid  # TODO: Use mid point instead of centroid
        x_offset = target.x - text_center.x
        y_offset = target.y - text_center.y
        new_elements = []
        for poly in self.polygons:
            new = affinity.translate(poly, xoff=x_offset, yoff=y_offset)
            new_elements.append(new)
        self.polygons = new_elements

    def move_and_fit_box(self, rectangle):
        w, _, angle = utils.width_angle(rectangle)
        factor = w / self.width
        self.scale(factor)
        self.translate_to(rectangle.centroid)
        self.rotate(angle)
