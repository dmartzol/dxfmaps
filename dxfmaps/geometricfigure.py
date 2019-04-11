from dxfmaps import utils
from dxfmaps import projections
from dxfmaps import fonts
import shapely
from shapely.geometry import shape
import ezdxf


class GeometricFigure:
    def __init__(self, multipolygon):
        self.multipolygon = multipolygon
        self.units = "mm"
        self.scaling_factor = None

    @property
    def centroid(self):
        return self.multipolygon.centroid

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
        return self.multipolygon.bounds

    def simplify(self, tolerance=2000, verbose=False):
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

    def translate_to_center(self):
        """
        Translates all the geometries to the origin (0, 0)
        """
        minx, miny, maxx, maxy = self.bounds
        x_offset = - min(minx, maxx)
        y_offset = - min(miny, maxy)
        self.multipolygon = shapely.affinity.translate(
            self.multipolygon,
            xoff=x_offset,
            yoff=y_offset
        )

    def scale_to_width(self, target_width):
        """
        Scales the geometries to a specific width
        """
        self.scaling_factor = target_width / self.width
        self.multipolygon = shapely.affinity.scale(
            self.multipolygon,
            xfact=self.scaling_factor,
            yfact=self.scaling_factor,
            origin=(0, 0)
        )

    def scale_to_height(self, target_height):
        """
        Scales the geometries to a specific heigh
        """
        self.scaling_factor = target_height / self.height
        self.multipolygon = shapely.affinity.scale(
            self.multipolygon,
            xfact=self.scaling_factor,
            yfact=self.scaling_factor,
            origin=(0, 0)
        )

    def to_svg(self, filename='out.svg', stroke_width=.2, back_buffered=False):
        utils.save_svg(
            self.multipolygon,
            filename=filename,
            width=self.width,
            units=self.units,
            stroke_width=stroke_width
        )
        if back_buffered:
            interior = self.multipolygon.buffer(0.5, cap_style=2, join_style=1)
            interior = interior.buffer(-1.0, cap_style=2, join_style=1)
            utils.save_svg(
                interior,
                filename='buffered.svg',
                width=self.width,
                units=self.units,
                stroke_width=stroke_width
            )

    def to_dxf(self, filename='out.dxf'):
        drawing = ezdxf.new('R2000')
        modelspace = drawing.modelspace()
        if isinstance(self.multipolygon, shapely.geometry.MultiPolygon):
            for polygon in self.multipolygon.geoms:
                vertices = list(polygon.exterior.coords)
                modelspace.add_lwpolyline(vertices)
        elif isinstance(self.multipolygon, shapely.geometry.Polygon):
            polygon = self.multipolygon
            vertices = list(polygon.exterior.coords)
            modelspace.add_lwpolyline(vertices)
        drawing.saveas(filename)
