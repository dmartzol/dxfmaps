import shapely
import time
import random
from operator import attrgetter
import math

WORLD_COUNTRIES = "../shapefiles/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"
WORLD_PROVINCES = '/shapefiles/ne_10m_admin_1_states_provinces/ne_10m_admin_1_states_provinces.shp'


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
    If object is a Multipolygon, returns its biggest(in area) polygon
    """
    if isinstance(geometry, shapely.geometry.polygon.Polygon):
        return geometry
    elif isinstance(geometry, shapely.geometry.multipolygon.MultiPolygon):
        return max_area_polygon(geometry)
    else:
        raise Exception('Non valid geometry')


def centroid_as_polygon(polygon, relative_size=0.05):
    """
    Returns a round "small" shapely.polygon that represents the centroid of the
    given polygon. The size of the returned polygon is given relatively to the
    longest side of polygon.
    """
    w, h = size_of_rotated_rectangle(polygon)
    c = max(h, w) * relative_size
    return polygon.centroid.buffer(c)


def freetype_nodes():
    """
    https://stackoverflow.com/questions/12061882/render-vector-letter-in-python
    """


def angle_of_rotated_rectangle(rectangle):
    """
    Returns the angle of a rotated rectangle.
    """
    x0, y0 = rectangle.exterior.coords[0]
    x1, y1 = rectangle.exterior.coords[1]
    angle = math.atan2(y1-y0, x1-x0)
    return angle


def distance(point0, point1):
    """
    Returns the distance between two points given as tuples
    """
    x0, y0 = point0
    x1, y1 = point1
    return math.hypot(x0-x1, y0-y1)


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


def inner_rectangle(polygon):
    """
    Returns a shapely box contained in a given polygon.
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


def scale_adjust(n):
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


def save_svg(full_map, filename='out.svg', stroke_width=1.0, width=500, units="px"):
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
