from dxfmaps import utils
from dxfmaps import projections
from dxfmaps import fonts
import shapely
from shapely.geometry import shape
import ezdxf
import cairocffi as cairo


class GeometricFigure:
    def __init__(self, elements):
        self.elements = elements
        self.units = "mm"
        self.scaling_factor = None

    @property
    def as_multipolygon(self):
        all_polygons = []
        for element in self.elements:
            all_polygons.extend(element.as_polygons())
        return shapely.geometry.MultiPolygon(all_polygons)

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
        return self.as_multipolygon.bounds

    @property
    def nodes_count(self):
        return sum([x.nodes_count for x in self.elements])

    def simplify(self, tolerance=2000, verbose=True):
        """
        Removes nodes from the path of every polygon according to tolerance
        """
        self.elements = [x.simplify(tolerance) for x in self.elements]
        if verbose:
            print("{} nodes.".format(self.nodes_count))

    def translate_to_center(self):
        """
        Translates all the geometries to the origin (0, 0)
        """
        minx, miny, maxx, maxy = self.bounds
        x_offset = - min(minx, maxx)
        y_offset = - min(miny, maxy)
        new_elements = []
        for element in self.elements:
            new_elements.append(element.translate(x_offset, y_offset))
        self.elements = new_elements

    def scale_to_width(self, target_width):
        """
        Scales the geometries to a specific width
        """
        self.scaling_factor = target_width / self.width
        new_elements = []
        for element in self.elements:
            new_elements.append(element.scale_to_width(self.scaling_factor))
        self.elements = new_elements

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

    def to_png(self, filename='out.png', stroke_width=1.0):
        height = int(self.height)
        width = int(self.width)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        context = cairo.Context(surface)
        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.set_line_join(cairo.LINE_JOIN_ROUND)
        context.set_line_width(stroke_width)
        with context:
            context.set_source_rgb(1, 1, 1)
            context.paint()
        # Cairo coordinate system is on the upper left corner, so
        # we need to do a vertical flip first
        multipolygon = utils.vertical_flip(self.as_multipolygon)
        for polygon in multipolygon:
            vertices = polygon.exterior.coords
            x, y = vertices[0]
            context.move_to(x, y)
            for vertex in vertices:
                x, y = vertex
                context.line_to(x, y)
        context.stroke()
        surface.write_to_png(filename)
