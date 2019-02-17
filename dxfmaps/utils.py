import shapely
import time
import random
from operator import attrgetter

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


def centroid_as_polygon(polygon, p=0.1):
    """
    Returns a polygon that represents the centroid of a given polygon
    """
    c = polygon.area * p
    return polygon.centroid.buffer(c)


def inner_rectangle(polygon):
    """
    Returns a shapely box contained in a given polygon.
    """
    p = 0.02
    increment = polygon.area * -0.006
    print(increment)
    buffered = polygon.buffer(increment, 1)
    while True:
        if isinstance(buffered, shapely.geometry.MultiPolygon):
            buffered = max_area_polygon(buffered)
        if polygon.contains(buffered.minimum_rotated_rectangle):
            print("Square break")
            break
        if p * polygon.area > buffered.area:
            print("Area break")
            break
        buffered = buffered.buffer(increment, 1)
    return buffered.minimum_rotated_rectangle


def scale_adjust(n):
    return -1.3624*(0.001 - n)


def list_of_countries(sf):
    for x in sf.shapeRecords():
        print("Name: {} ({})".format(x.record["NAME"], x.record.oid))


def list_of_continents(sf):
    print("\n Continents available: ")
    continents = set()
    for x in sf.shapeRecords():
        continents.add(x.record["CONTINENT"])
    for item in continents:
        print(item)
    print()


def item_info(sf, row, field=None):
    """
    Prints every field and its values for the item in the specified row of the shapefile.
    """
    fields = [item[0] for item in sf.fields[1:]]
    record = sf.record(row)
    if field:
        print("{}: {}".format(fields[field], record[field]))
    else:
        for i, field in enumerate(fields):
            print("{} - {}: {}".format(i, field, record[field]))


def countries_by_continent(sf, continent):
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
