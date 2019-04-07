import shapely
import shapely.wkt
from dxfmaps import utils
from dxfmaps.fonts import *


def label(polygon, name):
    inner_rectangle = utils.inner_rectangle(polygon)
    cir_centroid = utils.centroid_as_polygon(inner_rectangle)
    text = Text(name)
    rendered_text = text.polygons
    return [inner_rectangle, cir_centroid, rendered_text]


class Text:
    def __init__(self, string, font=VERA):
        self.string = string
        self.font = font
        self.polygons = self._build_polygons()
        self._load_polygons()

    def _build_polygons(self):
        string = self.string
        font = self.font
        polygons = []
        for char in string:
            if char not in font:
                raise ValueError("Character {} not in {}".format(char, font))
            for geom in font[char]:
                polygons.append(shapely.wkt.loads(geom))
        return polygons

    def _load_polygons(self):
        string = self.string
        font = self.font
        text_dict = {}
        for char in string:
            if char not in font:
                raise ValueError("Character {} not in {}".format(char, font))
            geom = shapely.wkt.loads(font[char])
            text_dict[char] = multipol
        return None

    def move_to(self, point):
        pass

    def scale_to_fit(self, rectangle):
        pass
