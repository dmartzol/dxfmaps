import shapely
from shapely import geometry
from shapely import  affinity
from dxfmaps import projections


class NamedGeometry:
    """
    Class stores a geometry and its name.

    Args:
        geometry: Shapely Polygon or MultiPolygon
        name (str, optional): the name given to the geometry

    Attributes:
        type:
        is_multipolygon
        is_polygon
        bounds
        nodes_count
        as_polygons
        scale_to_width
        translate
        filter_by_area
        simplify
        project
    """

    def __init__(self, geometry, name=None, tag=None):
        if geometry is None:
            raise ValueError("NamedGeometry needs a geometry")
        self.geometry = geometry
        self.name = name
        self.tag = tag

    @property
    def type(self):
        if self.is_polygon:
            return 'Polygon'
        elif self.is_multipolygon:
            return 'MultiPolygon'

    @property
    def is_multipolygon(self):
        return isinstance(
            self.geometry,
            geometry.multipolygon.MultiPolygon
        )

    @property
    def is_polygon(self):
        return isinstance(
            self.geometry,
            geometry.polygon.Polygon
        )

    @property
    def bounds(self):
        return self.geometry.bounds

    @property
    def nodes_count(self):
        count = 0
        for poly in self.as_polygons():
            count += len(poly.exterior.coords)
        return count

    def as_polygons(self):
        if self.is_polygon:
            return [self.geometry]
        elif self.is_multipolygon:
            return list(self.geometry)
        else:
            print(type(self.geometry))
            msg = '{} is neither polygon or multipolygon'.format(self.name)
            raise TypeError(msg)

    def scale(self, scaling_factor):
        geometry = affinity.scale(
                    self.geometry,
                    xfact=scaling_factor,
                    yfact=scaling_factor,
                    origin=(0, 0)
                )
        copy = NamedGeometry(geometry, name=self.name)
        return copy

    def translate(self, x_offset, y_offset):
        geometry = affinity.translate(
            self.geometry,
            xoff=x_offset,
            yoff=y_offset
        )
        copy = NamedGeometry(geometry, name=self.name)
        return copy

    def rotate(self, angle):
        geometry = affinity.rotate(
            self.geometry,
            angle,
            use_radians=False
        )
        copy = NamedGeometry(geometry, name=self.name)
        return copy

    def filter_by_area(self, limit):
        """
        Returns a NamedGeometry object with the geometris that
        are larger in area than the given limit. If none of them is
        larger, returns None
        """
        def big(polygon):
            return polygon.area > limit
        if self.is_polygon:
            if self.geometry.area > limit:
                return self
            return None
        elif self.is_multipolygon:
            filtered = [x for x in self.geometry if big(x)]
            if filtered is None:
                return None
            multi = shapely.geometry.MultiPolygon(filtered)
            copy = NamedGeometry(multi, name=self.name)
            return copy
        else:
            raise ValueError("We have a weird geometry")

    def simplify(self, tolerance):
        new = self.geometry.simplify(tolerance)
        copy = NamedGeometry(new, name=self.name)
        return copy

    def project(self, projection_name):
        new_polygons = []
        for polygon in self.as_polygons():
            new_coords = []
            for coords in polygon.exterior.coords:
                x, y = getattr(projections, projection_name)(*coords)
                new_coords.append([x, y])
            new_polygons.append(shapely.geometry.Polygon(new_coords))
        if len(new_polygons) > 1:
            multi = shapely.geometry.MultiPolygon(new_polygons)
            copy = NamedGeometry(multi, name=self.name)
            return copy
        elif len(new_polygons) == 1:
            copy = NamedGeometry(new_polygons[0], name=self.name)
            return copy
