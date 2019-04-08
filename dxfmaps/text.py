import shapely
import shapely.wkt
from dxfmaps import utils
from dxfmaps.fonts import *


def label(polygon, name, box=True, centroid=True):
    polygons = []
    inner_rectangle = utils.inner_rectangle(polygon)
    cir_centroid = utils.centroid_as_polygon(inner_rectangle)
    if box:
        polygons.append(inner_rectangle)
    if centroid:
        polygons.append(cir_centroid)
    text = Text(name)
    rendered_text = text.multipolygon
    polygons.extend(rendered_text)
    return polygons


class Text:
    def __init__(self, string, font=WALKWAY_BOLD):
        self.string = string
        self.font = font
        self.multipolygon = self._build_multipolygon()

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

    def move_center_to(self, point):
        pass

    def rotate_to_fit(self, rectangle):
        pass
