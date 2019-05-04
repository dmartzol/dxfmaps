import shapely
from shapely import affinity
from shapely import geometry
from dxfmaps import projections
from dxfmaps import utils
from dxfmaps.rectangle import mrcd
from .text import Text


class Country:
    """
    Attributes:
        self.contours: List of shapely polygons defining the contour of the country
        self.name: The name of the country
    """
    def __init__(self, contours_list, name, labels=[]):
        self.contours = contours_list
        self.name = name
        self.labels = labels

    @property
    def as_multipolygon(self):
        return shapely.geometry.MultiPolygon(self.contours)

    @property
    def bounds(self):
        return self.as_multipolygon.bounds

    @property
    def nodes_count(self):
        count = 0
        for poly in self.contours:
            count += len(poly.exterior.coords)
        return count

    def filter_by_area(self, limit):
        def big(p):
            return p.area > limit
        new_polygons = [x for x in self.contours if big(x)]
        return Country(new_polygons, self.name)

    def scale(self, scaling_factor):
        new_polygons = []
        for polygon in self.contours:
            new_polygon = affinity.scale(
                        polygon,
                        xfact=scaling_factor,
                        yfact=scaling_factor,
                        origin=(0, 0)
                    )
            new_polygons.append(new_polygon)
        return Country(new_polygons, name=self.name)

    def translate(self, x_offset, y_offset):
        new_polygons = []
        for polygon in self.contours:
            new_polygon = affinity.translate(
                polygon,
                xoff=x_offset,
                yoff=y_offset
            )
            new_polygons.append(new_polygon)
        return Country(new_polygons, name=self.name)

    def project(self, projection_name):
        new_polygons = []
        for polygon in self.contours:
            new_coords = []
            for coords in polygon.exterior.coords:
                x, y = getattr(projections, projection_name)(*coords)
                new_coords.append([x, y])
            new_polygons.append(geometry.Polygon(new_coords))
        return Country(new_polygons, self.name)

    def simplify(self, tolerance):
        new_elements = []
        for polygon in self.contours:
            new_elements.append(polygon.simplify(tolerance))
        return Country(new_elements, self.name)

    def generate_labels(self, box, centroid, uppercase, n, verbose=True):
        if verbose:
            print("Generating labels for {}".format(self.name))
        new_polygons = []
        name = self.name
        for polygon in self.contours:
            if uppercase:
                name = name[0].upper() + name[1:]
            text = Text(name)
            ratio = text.width / text.height
            inner_rectangles = []
            while len(inner_rectangles) == 0:
                print("Trying {} with {} points".format(self.name, n))
                inner_rectangles = mrcd(polygon, n=n, ratio=ratio)
                n += 5
            rectangle = inner_rectangles[0]
            text.move_and_fit_box(rectangle)
            # rectangle = utils.rectangle(polygon)
            if box:
                new_polygons.append(rectangle)
            if centroid:
                cir_centroid = utils.centroid_as_polygon(rectangle)
                new_polygons.append(cir_centroid)
            new_polygons.extend(text.polygons)
        self.labels = new_polygons
