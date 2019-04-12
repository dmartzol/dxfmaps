import shapely
import shapely.wkt
from dxfmaps import utils
from .geometricfigure import GeometricFigure
from .fonts import *


def label(polygon, name, box=False, centroid=False, uppercase=True):
    polygons = []
    inner_rectangle = utils.inner_rectangle(polygon)
    cir_centroid = utils.centroid_as_polygon(inner_rectangle)
    if box:
        polygons.append(inner_rectangle)
    if centroid:
        polygons.append(cir_centroid)
    if uppercase:
        name = name[0].upper() + name[1:]
    text = Text(name)
    text.move_and_fit_box(inner_rectangle)
    rendered_text = text.multipolygon
    polygons.extend(rendered_text)
    return polygons


class Text(GeometricFigure):
    def __init__(self, string, font=VERA, spacing=100.0):
        self.string = string
        self.font = font
        self.spacing = spacing
        return super().__init__(self._as_multipolygon())

    def _as_multipolygon(self):
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
                geom = shapely.affinity.translate(geom, xoff=x_offset)
            _, _, maxx, _ = geom.bounds
            right_bounds.append(maxx)
            geoms.append(geom)
        polygons_list = []
        for geom in geoms:
            if isinstance(geom, shapely.geometry.MultiPolygon):
                for polygon in geom:
                    polygons_list.append(polygon)
            elif isinstance(geom, shapely.geometry.Polygon):
                polygons_list.append(geom)
        multipolygon = shapely.geometry.MultiPolygon(polygons_list)
        return multipolygon

    def _scale(self, factor):
        self.multipolygon = shapely.affinity.scale(
            self.multipolygon,
            xfact=factor,
            yfact=factor
        )

    def _translate_to(self, target):
        text_center = self.centroid
        x_offset = target.x - text_center.x
        y_offset = target.y - text_center.y
        self.multipolygon = shapely.affinity.translate(
            self.multipolygon,
            xoff=x_offset,
            yoff=y_offset
        )

    def _rotate(self, angle):
        self.multipolygon = shapely.affinity.rotate(
            self.multipolygon,
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
