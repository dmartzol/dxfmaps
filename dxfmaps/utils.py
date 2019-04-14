import shapely
import time
import random
from operator import attrgetter
import math

WORLD_COUNTRIES = "../shpf/10m-0-countries/ne_10m_admin_0_countries.shp"
WORLD_PROVINCES = ("/shpf/10m-1-states-provinces/"
                   "ne_10m_admin_1_states_provinces.shp")

# TODO: Separate into geometry.py


def greatest_contained_rectangle(polygon, points_count=20):
    """
    Returns the rectangle with greatest area contained in polygon.
    See:
    http://d3plus.org/blog/behind-the-scenes/2014/07/08/largest-rect/
    """
    start = time.time()
    print(len(polygon.exterior.coords))
    p = len(polygon.exterior.coords) * 0.15
    tolerance = 0
    while len(polygon.exterior.coords) > p:
        tolerance += 0.001
        polygon = polygon.simplify(tolerance)
    points = []
    for i in range(points_count):
        points.append(random_point_in(polygon))
    print(points)
    end = time.time()
    print("It took {0:.2f} seconds".format(end-start))
    return polygon


def inner_rectangle(polygon):
    """Returns a shapely box contained in a given polygon.

    This is not the largest contained box, but it is a relatively large box
    that is guaranteed to be contained in the given polygon. This is faster
    than finding the largest contained box.
    """
    p = 0.02
    increment = reduction_increment(polygon)
    buffered = polygon.buffer(increment, 1)
    while True:
        if isinstance(buffered, shapely.geometry.MultiPolygon):
            buffered = max_area_polygon(buffered)
        if polygon.contains(buffered.minimum_rotated_rectangle):
            break
        if p * polygon.area > buffered.area:
            print("Area break")
            break
        buffered = buffered.buffer(increment, 1)
    return buffered.minimum_rotated_rectangle


def vertical_flip(geometry):
    """
    Return a vertical reflection/flip of geometry.

    rtype: shapely.geometry.MultiPolygon
    """
    if not isinstance(geometry, shapely.geometry.MultiPolygon):
        raise ValueError("Argument must be a multipolygon")
    result = shapely.affinity.scale(
        geometry,
        xfact=1.0,
        yfact=-1.0
    )
    return result


def random_point_in(polygon):
    """
    Returns a random point inside the given polygon
    """
    minx, miny, maxx, maxy = polygon.envelope.bounds
    while True:
        x = random.uniform(minx, maxx)
        y = random.uniform(miny, maxy)
        if polygon.contains(shapely.geometry.Point(x, y)):
            return (x, y)


def max_area_polygon(multipolygon):
    """
    Returns the polygon with greatest area inside a multipolygon
    """
    # TODO - Try without using attrgetter
    return max(multipolygon, key=attrgetter('area'))


def multipolygon_to_polygon(geometry):
    """
    If object is a Polygon, returns the object unmodified.
    If object is a Multipolygon, returns its biggest(in area) polygon.
    This means this function gives only 1 polygon for each country.
    This will have to be fixed later.
    """
    if isinstance(geometry, shapely.geometry.polygon.Polygon):
        return geometry
    elif isinstance(geometry, shapely.geometry.multipolygon.MultiPolygon):
        return max_area_polygon(geometry)
    else:
        raise Exception('Non valid geometry')


def get_polygons(geometry):
    """
    If geometry is a polygon, returns a list with geometry as its
    only element.
    If geometry is a multipolygon, returns a list of its polygons.
    """
    if isinstance(geometry, shapely.geometry.polygon.Polygon):
        return [geometry]
    elif isinstance(geometry, shapely.geometry.multipolygon.MultiPolygon):
        return list(geometry)
    else:
        raise Exception('Non valid geometry')


def centroid_as_polygon(rectangle, relative_size=0.05):
    """
    Returns a round shapely.polygon that represents the centroid of the
    given rectangle. The size of the returned circle is proportional to
    the longest side of the rectangle.
    """
    w, h = size_of_rotated_rectangle(rectangle)
    c = max(h, w) * relative_size
    return rectangle.centroid.buffer(c)


def freetype_nodes():
    """
    https://stackoverflow.com/questions/12061882/render-vector-letter-in-python
    """

# TODO: Deprecated
def rectangle_angle(rectangle):
    """
    Returns the angle in radians of a rotated rectangle.
    """
    x0, y0 = rectangle.exterior.coords[0]
    x1, y1 = rectangle.exterior.coords[1]
    angle = math.atan2(y1-y0, x1-x0)
    return math.degrees(angle)


def distance(pointA, pointB):
    """
    Returns the distance between two points given as tuples
    """
    x0, y0 = pointA
    x1, y1 = pointB
    return math.hypot(x0-x1, y0-y1)


def slope(point_A, point_B):
    x0, y0 = point_A
    x1, y1 = point_B
    if x0 == x1:
        return None
    return (y1-y0)/(x1-x0)


def slope_angle(slope):
    """
    Returns the angle(in degrees) of a line given its slope
    """
    if slope is None:
        return 90
    return math.degrees(math.atan(slope))


def line_angle(point_A, point_B):
    """
    Returns the angle(in degrees) of a line given 2 points from it
    """
    line_slope = slope(point_A, point_B)
    angle = slope_angle(line_slope)
    return angle


def width_angle(rectangle):
    """Returns the length and angle(in degrees) of the longest side of a
    rotated rectangle
    """
    point_A, point_B, point_C = rectangle.exterior.coords[:3]
    w = distance(point_A, point_B)
    h = distance(point_B, point_C)
    if w > h:
        angle = line_angle(point_A, point_B)
        return w, angle
    angle = line_angle(point_B, point_C)
    return h, angle


def size_of_rotated_rectangle(rectangle):
    """
    Returns the width and height of a rotated rectangle given as a
    shapely polygon. Width and Height are not parallel to the axes.
    """
    point0, point1, point2 = rectangle.exterior.coords[:3]
    width = distance(point0, point1)
    height = distance(point1, point2)
    return width, height


def reduction_increment(polygon, ratio=0.01):
    """
    Calculates a fraction of the width or height of a rotated rectangle.
    This increment is used in a shapely buffer method to reduce the size of a
    polygon in a more convenient way.
    """
    w, h = size_of_rotated_rectangle(polygon.minimum_rotated_rectangle)
    increment = max(h, w) * -ratio
    return increment


def scale_adjust(n):  # TODO: Deprecated
    """
    Adjusting scale of text in a DXF layer
    """
    return -1.3624*(0.001 - n)


def list_of_countries(sf):
    for x in sf.shapeRecords():
        print("Name: {} ({})".format(x.record["NAME"], x.record.oid))


def list_of_continents(sf):
    """
    Prints a list of the continents in the shapefile.
    """
    print("\n Continents available: ")
    continents = set()
    for x in sf.shapeRecords():
        continents.add(x.record["CONTINENT"])
    for item in continents:
        print(item)
    print()


def item_info(sf, row, field=None):
    """
    Prints every field and its values for the item in the specified row of the
    shapefile.
    """
    fields = [item[0] for item in sf.fields[1:]]
    record = sf.record(row)
    if field:
        print("{}: {}".format(fields[field], record[field]))
    else:
        for i, field in enumerate(fields):
            print("{} - {}: {}".format(i, field, record[field]))


def countries_by_continent(sf, continent):
    """
    Prints a list of countries that match the specified continent in the
    shapefile.
    """
    records = sf.records()
    for item in records:
        if item['CONTINENT'] == continent:
            print(item["NAME"], item.oid)


def save_svg(full_map, filename='out.svg', stroke_width=1.0, width=500, units="px"):  # TODO: Rename to ~geom2svg
    size_and_units = "{}{}".format(str(width), units)
    poligon_template = "\n<polygon stroke=\"black\" stroke-width=\"{}\" fill=\"none\" points=\"{} \"/>\n"
    file = open(filename, 'w')
    svg_style = "<svg xmlns=\"http://www.w3.org/2000/svg\" version=\"1.1\" width=\"{}\" height=\"{}\" viewBox=\"{} {} {} {}\"> \n"
    file.write(svg_style.format(size_and_units, size_and_units, 0, 0, full_map.bounds[2], full_map.bounds[3]))
    file.write("<g transform=\"translate(0,{}) scale(1,-1)\">\n".format(full_map.bounds[3]))
    list_of_coords = []
    if isinstance(full_map, shapely.geometry.multipolygon.MultiPolygon):
        for polygon in full_map.geoms:
            for x, y in polygon.exterior.coords:
                list_of_coords.append("{},{}".format(x, y))
            file.write(poligon_template.format(stroke_width, " ".join(list_of_coords)))
            list_of_coords = []
    if isinstance(full_map, shapely.geometry.polygon.Polygon):
        polygon = full_map
        for x, y in polygon.exterior.coords:
            list_of_coords.append("{},{}".format(x, y))
        file.write(poligon_template.format(stroke_width, " ".join(list_of_coords)))
    file.write("</g>\n")
    file.write("</svg>")
    file.close()
