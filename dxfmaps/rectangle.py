from shapely.geometry import Polygon, MultiPolygon, Point, LineString
from shapely.affinity import rotate, translate
from typing import List
import math


def mrcd(polygon: Polygon, n=20, ratio=None) -> List[Polygon]:
    """
    Finding the largest area rectangle of arbitrary orientation in
    a closed contour.
    Rubén Molano, Pablo G. Rodriguez, Andres Caro, M. Luisa Duran.

    :param ratio:
    :param n:
    :param polygon: shapely Polygon
    :return: shapely Polygon
    """
    # Get the minimum rotated rectangle and rotate it so it is parallel
    # to the axes
    envelope = polygon.minimum_rotated_rectangle
    centroid = envelope.centroid
    a, b, angle = width_angle(polygon.minimum_rotated_rectangle)
    polygon = rotate(polygon, -angle, origin=centroid)
    # We translate everything to (0, 0)
    minx, miny, maxx, maxy = polygon.bounds
    polygon = translate(polygon, xoff=-minx, yoff=-miny)
    # Now we get the greatest contained rectangles
    rect_list = mir(polygon, n, ratio)
    rectangles = []
    for rectangle in rect_list:
        rectangle = translate(rectangle, xoff=minx, yoff=miny)
        rectangle = rotate(rectangle, angle, origin=centroid)
        rectangles.append(rectangle)
    return rectangles


def mir(polygon: Polygon, resolution: int, ratio: float) -> List[Polygon]:
    """

    :param ratio:
    :param polygon:
    :param resolution: number of points per side
    :return: List[Polygon]
    """
    envelope = polygon.envelope
    minx, miny, maxx, maxy = envelope.bounds
    L = max(maxx, maxy) / resolution
    points = compute_points(polygon, resolution)
    u = compute_u(polygon, points)
    n = len(points)
    max_area = 0
    rectangles = []
    for i in range(1, n - 2):
        for j in range(i + 1, n - 1):
            if u[i][j] != 0:
                for k in range(j + 1, n):
                    if u[i][k] != 0 and perpendicular(u[i][j], u[i][k]):
                        point = get_opposite_point(points, j, i, k)
                        rect_points = [points[i], points[k], point, points[j]]
                        rectangle = Polygon([[p.x, p.y] for p in rect_points])
                        if ratio is not None:
                            if not fullfills_ratio(rectangle, ratio):
                                continue
                        if polygon.contains(rectangle):
                            if rectangle.area > max_area:
                                max_area = rectangle.area
                                rectangles.clear()
                                rectangles.append(rectangle)
                            if rectangle.area == max_area:
                                rectangles.append(rectangle)
    return rectangles


def compute_u(polygon: Polygon, points: List[Point]) -> List[List[Point]]:
    n = len(points)
    matrix_u = [[0 for _ in range(n)] for _ in range(n)]
    for i in range(1, n):
        for j in range(1, n):
            if i >= j:
                continue
            else:
                a = points[i]
                b = points[j]
                segment = LineString([a, b])
                if polygon.contains(segment):
                    matrix_u[i][j] = Point(b.x - a.x, b.y - a.y)
    return matrix_u


def fullfills_ratio(rectangle: Polygon, target_ratio: float, margin=0.1):
    minx, miny, maxx, maxy = rectangle.bounds
    w, h = maxx - minx, maxy - miny
    if w == 0 or h == 0:
        return False
    current_ratio = w / h
    if target_ratio - margin <= current_ratio <= target_ratio + margin:
        return True
    return False


def get_opposite_point(points: List[Point], j, i, k):
    j = points[j]
    i = points[i]
    k = points[k]
    result = Point(j.x - i.x + k.x, j.y - i.y + k.y)
    return result


def compute_points(polygon: Polygon, n) -> List[Point]:
    rectangle = polygon.envelope
    _, _, maxx, maxy = rectangle.bounds
    l = max(maxx, maxy) / n
    points = []
    for j in range(n + 1):
        for i in range(n + 1):
            point = Point(l * i, l * j)
            if polygon.contains(point):
                points.append(point)
    return points


def perpendicular(a: Point, b: Point) -> bool:
    dot = a.x * b.x + a.y * b.y
    return bool(dot == 0)


def distance(point_a, point_b):
    """
    Returns the distance between two points given as tuples
    """
    x0, y0 = point_a
    x1, y1 = point_b
    return math.hypot(x0 - x1, y0 - y1)


def width_angle(rectangle: Polygon):
    """Returns the length and angle(in degrees) of the longest side of a
    rotated rectangle
    """
    point_a, point_b, point_c = rectangle.exterior.coords[:3]
    a = distance(point_a, point_b)
    b = distance(point_b, point_c)
    if a > b:
        angle = line_angle(point_a, point_b)
        return a, b, angle
    angle = line_angle(point_b, point_c)
    return b, a, angle


def line_angle(point_a, point_b):
    """
    Returns the angle(in degrees) of a line given 2 points from it
    """
    line_slope = slope(point_a, point_b)
    angle = slope_angle(line_slope)
    return angle


def slope(point_a, point_b):
    x0, y0 = point_a
    x1, y1 = point_b
    if x0 == x1:
        return None
    return (y1 - y0) / (x1 - x0)


def slope_angle(slope):
    """
    Returns the angle(in degrees) of a line given its slope
    """
    if slope is None:
        return 90
    return math.degrees(math.atan(slope))
