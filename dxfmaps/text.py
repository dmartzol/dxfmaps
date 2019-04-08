import shapely
import shapely.wkt
from dxfmaps import utils
from dxfmaps.fonts import *


def label(polygon, name, box=True, centroid=False):
    polygons = []
    inner_rectangle = utils.inner_rectangle(polygon)
    cir_centroid = utils.centroid_as_polygon(inner_rectangle)
    if box:
        polygons.append(inner_rectangle)
    if centroid:
        polygons.append(cir_centroid)
    text = Text(name)
    text.move_and_fit_box(inner_rectangle)
    rendered_text = text.geometry
    polygons.extend(rendered_text)
    return polygons


class Text:
    def __init__(self, string, font=VERA):
        self.string = string
        self.font = font
        self.geometry = self._build_multipolygon()

    @property
    def centroid(self):
        return self.geometry.centroid

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
        return self.geometry.bounds

    def _build_multipolygon(self, spacing=0):
        string = self.string
        font = self.font
        polygons = []
        right_bounds = []
        for char in string:
            if char not in font:
                raise ValueError("Character {} not in {}".format(char, font))
            geom = shapely.wkt.loads(font[char])
            minx, _, _, _ = geom.bounds
            if right_bounds:
                x_offset = right_bounds[-1] - minx + spacing
                geom = shapely.affinity.translate(geom, xoff=x_offset)
            _, _, maxx, _ = geom.bounds
            right_bounds.append(maxx)
            polygons.append(geom)
        multipolygon = shapely.geometry.MultiPolygon(polygons)
        return multipolygon

    def _scale(self, factor):
        self.geometry = shapely.affinity.scale(
            self.geometry,
            xfact=factor,
            yfact=factor
        )

    def _translate_to(self, target):
        text_center = self.centroid
        x_offset = target.x - text_center.x
        y_offset = target.y - text_center.y
        self.geometry = shapely.affinity.translate(
            self.geometry,
            xoff=x_offset,
            yoff=y_offset
        )

    def _rotate(self, angle):
        self.geometry = shapely.affinity.rotate(
            self.geometry,
            angle,
            use_radians=False
        )

    def move_and_fit_box(self, rectangle):
        rectangle_w = max(utils.size_of_rotated_rectangle(rectangle))
        l, angle = utils.width_angle(rectangle)
        factor = rectangle_w / self.width
        self._scale(factor)
        self._translate_to(rectangle.centroid)
        self._rotate(angle)
