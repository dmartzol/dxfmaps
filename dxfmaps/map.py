import shapefile
import shapely
import cairocffi as cairo
import ezdxf
from shapely import geometry
from shapely.geometry import Polygon, MultiPolygon
from typing import List, Tuple
from .country import Country
from .utils import get_polygons, vertical_flip, polygons_to_svg

# TODO: Separate information methods in a different class


class Map:
    def __init__(self, path, continent=None, countries_set=None,
                 country_field='NAME', units='px'):
        """
        :param path: string specifying the path to the shapefile
        :param continent: name to plot its countries
        :param countries_set: set of countries you want to include in the map
        :param country_field: name of the field in the shapefile that contains countries geometries
        :param units: units to use for the output
        """
        sf = shapefile.Reader(path)
        self.sf = sf
        self.units = units
        self.country_field = country_field
        self.check_shapefile()
        self.continent = continent
        self.countries_set = countries_set
        if countries_set is not None:
            self.countries_set = {x.lower() for x in countries_set}
        self.countries = self.build_countries()
        self.scaling_factor = None

    @property
    def as_polygons(self) -> List[Polygon]:
        """Return the contours of all countries as a list of     shapely polygons
        :return: list of shapely polygons
        """
        all_polygons = []
        for country in self.countries:
            all_polygons.extend(country.contours)
        return all_polygons

    @property
    def labels_as_polygons(self) -> List[Polygon]:
        """Return the labels of all countries in a list of shapely polygons
        :return: list of labels as Shapely Polygons
        """
        all_polygons = []
        for country in self.countries:
            if country.labels:
                all_polygons.extend(country.labels)
        return all_polygons

    @property
    def as_multipolygon(self) -> MultiPolygon:
        """Return a shapely multipolygon containing all contours of the countries
        :return: Shapely MultiPolygon
        """
        return shapely.geometry.MultiPolygon(self.as_polygons)

    @property
    def bounds(self):
        """Return bounds of entire map as a 4 length tuple.

        :return: tuple minx, miny, maxx, maxy
        """
        return self.as_multipolygon.bounds

    @property
    def height(self) -> float:
        _, miny, _, maxy = self.bounds
        return maxy - miny

    @property
    def width(self) -> float:
        minx, _, maxx, _ = self.bounds
        return maxx - minx

    @property
    def nodes_count(self) -> int:
        """Calculate the number of all nodes of all the countries in the map.
        It does not include the nodes in the labels.

        :return: integer: Number of nodes in countries contours
        """
        return sum([x.nodes_count for x in self.countries])

    def check_shapefile(self) -> None:
        """Checks if all geometries read from the Shapefile are either Shapely
        Polygons or MultiPolygons. Raises TypeError if it finds a different
        geometry.

        :return: None
        """
        for shapeRecord in self.sf.shapeRecords():
            geom = geometry.shape(shapeRecord.shape.__geo_interface__)
            is_polygon = isinstance(
                geom,
                shapely.geometry.polygon.Polygon
            )
            is_multipolygon = isinstance(
                geom,
                shapely.geometry.multipolygon.MultiPolygon
            )
            if not (is_polygon or is_multipolygon):
                print(type(geom))
                name = shapeRecord.record[self.country_field]
                msg = "{} is not a valid geometry. It should not be included"
                raise TypeError(msg.format(name))

    def build_countries(self) -> List[Polygon]:
        """Return a list of polygons imported from the shapefile.

        First checks if the user used both conditions, countries and continent,
        to create the map. If so, it raises ValueError.

        Then creates the set of countries if a continent was given.

        Then it reads the countries from the shapefile.

        :return: list of Shapely Polygons
        """
        if self.countries_set and self.continent:
            raise ValueError("Cannot apply 2 filters.")
        elif self.continent:
            self.countries_set = self.get_countries(self.continent)
        countries = []
        for shapeRecord in self.sf.shapeRecords():
            name = shapeRecord.record[self.country_field].lower()
            if name in self.countries_set:
                geom = geometry.shape(shapeRecord.shape.__geo_interface__)
                countries.append(Country(get_polygons(geom), name))
        if not countries:
            raise ValueError("Not countries found")
        return countries

    def get_countries(self, continent: str) -> set:
        """Given a continent, return a set of countries pertaining to it
        according to the shapefile

        :param continent: Name of the continent
        :return: set of Shapely Polygons
        """
        countries_set = set()
        for shapeRecord in self.sf.shapeRecords():
            continent_in_record = shapeRecord.record["CONTINENT"].lower()
            if continent_in_record == continent:
                country_name = shapeRecord.record[self.country_field].lower()
                countries_set.add(country_name)
        if len(countries_set) == 0:
            raise ValueError("Continent not found")
        return countries_set

    def info(self):
        """Prints on screen some info about the current map.

        :return: None
        """
        print('-------- info --------')
        print("{} countries".format(len(self.countries)))
        for country in self.countries:
            count = len(country.contours)
            print("\t{} has {} geometries.".format(country.name, count))
            p = [x.area for x in country.contours]
            p.sort(reverse=True)
            for x in p:
                print("\t\t{0:.4f}".format(x))
            # for p in country.contours:
            #     print("\t\t Area {0:.4f}".format(p.area))

    def filter_by_area(self, area_limit=.5):
        new_countries = []
        for country in self.countries:
            new_country = country.filter_by_area(area_limit)
            if not new_country.contours:
                print("{} didn't pass the area filter.".format(country.name))
                continue
            new_countries.append(new_country)
        self.countries = new_countries

    def item_info(self, row, field=None):
        """Prints every field and its values for the item in the specified row
        of the shapefile.
        """
        fields = [item[0] for item in self.sf.fields[1:]]
        record = self.sf.record(row)
        if field:
            print("{}: {}".format(fields[field], record[field]))
        else:
            for i, field in enumerate(fields):
                print("{} - {}: {}".format(i, field, record[field]))

    def project(self, projection_name):
        """Transforms the current GPS coordinates to the chosen projection
        coordinates.

        Available projections:
            - Lambert Azimuthal Equal Area
            - Mercator
            - Winkel Tripel

        :param projection_name: Constant from .dxfmaps.utils
        :return: None
        """
        new_elements = []
        for country in self.countries:
            new_elements.append(country.project(projection_name))
        self.countries = new_elements

    def translate_to_center(self):
        """
        Translates all the geometries to the origin (0, 0)
        """
        minx, miny, maxx, maxy = self.bounds
        x_offset = - min(minx, maxx)
        y_offset = - min(miny, maxy)
        new_elements = []
        for country in self.countries:
            new_elements.append(country.translate(x_offset, y_offset))
        self.countries = new_elements

    def scale_to_width(self, target_width):
        """Scales the geometries to a specific width

        :param target_width:
        :return:
        """
        self.scaling_factor = target_width / self.width
        new_elements = []
        for country in self.countries:
            new_elements.append(country.scale(self.scaling_factor))
        self.countries = new_elements

    def simplify(self, tolerance=.0002, verbose=True):
        """
        Removes nodes from the path of every polygon according to tolerance

        :param tolerance:
        :param verbose:
        :return:
        """
        self.countries = [x.simplify(tolerance) for x in self.countries]
        if verbose:
            print("{} nodes.".format(self.nodes_count))

    def list_of_countries(self):
        for x in self.sf.shapeRecords():
            print("Name: {} ({})".format(
                x.record[self.country_field],
                x.record.oid)
            )

    def add_labels(self, box=False, centroid=False, uppercase=True):
        for country in self.countries:
            country.generate_labels(box, centroid, uppercase)

    def to_png(self, filename='out.png', stroke_width=1.0, white_bg=False):
        height = int(self.height)
        width = int(self.width)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        context = cairo.Context(surface)
        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.set_line_join(cairo.LINE_JOIN_ROUND)
        context.set_line_width(stroke_width)
        if white_bg:
            with context:
                context.set_source_rgb(1, 1, 1)
                context.paint()
        # Cairo coordinate system is on the upper left corner, so
        # we need to do a vertical flip first
        polygons = self.as_polygons
        polygons.extend(self.labels_as_polygons)
        polygons = vertical_flip(polygons)
        for polygon in polygons:
            vertices = polygon.exterior.coords
            x, y = vertices[0]
            context.move_to(x, y)
            for vertex in vertices:
                x, y = vertex
                context.line_to(x, y)
        context.stroke()
        surface.write_to_png(filename)

    def to_dxf(self, filename='out.dxf'):
        drawing = ezdxf.new('R2000')
        modelspace = drawing.modelspace()
        drawing.layers.new(name='Labels', dxfattribs={'color': 7})
        drawing.layers.new(name='Contours', dxfattribs={'color': 1})
        for country in self.countries:
            for polygon in country.contours:
                vertices = list(polygon.exterior.coords)
                modelspace.add_lwpolyline(
                    vertices,
                    dxfattribs={'layer': 'Contours'}
                )
            if country.labels:
                for polygon in country.labels:
                    vertices = list(polygon.exterior.coords)
                    modelspace.add_lwpolyline(
                        vertices,
                        dxfattribs={'layer': 'Labels'}
                    )
        drawing.saveas(filename)

    def to_svg(self, filename='out.svg', stroke=.5, buffered=False, labels=False):
        polygons = []
        polygons.extend(self.as_polygons)
        polygons.extend(self.labels_as_polygons)
        polygons_to_svg(
            polygons,
            filename=filename,
            width=self.width,
            units=self.units,
            stroke_width=stroke
        )
        if buffered:
            raise NotImplementedError("Buffered is not implemented yet")
            interior = self.multipolygon.buffer(0.5, cap_style=2, join_style=1)
            interior = interior.buffer(-1.0, cap_style=2, join_style=1)
            polygons_to_svg(
                interior,
                filename='buffered.svg',
                width=self.width,
                units=self.units,
                stroke_width=stroke_width
            )