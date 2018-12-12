import osmnx as ox
import shapely

def fetch(list_of_names):
    ox.config(use_cache=True)
    geodataframe = ox.gdf_from_places(list_of_names)
    return geodataframe

def project(geodataframe):
    return ox.project_gdf(geodataframe)


def dataframe2polygons(geodataframe):
    polygons = []
    for index, row in geodataframe.iterrows():
        if isinstance(row.geometry, shapely.geometry.multipolygon.MultiPolygon):
            for geom in row.geometry.geoms:
                polygons.append(geom)
        elif isinstance(row.geometry, shapely.geometry.polygon.Polygon):
            polygons.append(row.geometry)
        elif isinstance(row.geometry, shapely.geometry.linestring.LineString):
            print("")
            print("{} geometry is LineString".format(row.place_name))
            print("This linestring is ring: {}".format(row.geometry.is_ring))
            # TODO: Convert linestring to polygon
            # polygons.append(row.geometry)
        else:
            raise Exception('Found non valid geometry')
    return polygons

def filter_by_area(polygons, area_thresold = 1000000000):
    # TODO: Figure units for area!
    return [polygon for polygon in polygons if polygon.area > area_thresold]

def simplify(polygons, tolerance = 2000, verbose = False):
    # TODO: calculate adequate tolerance
    for i, polygon in enumerate(polygons):
        polygons[i] = shapely.geometry.Polygon(polygon.exterior.coords)
        nodes_before = len(list(polygon.exterior.coords))
        polygons[i] = polygons[i].simplify(tolerance=tolerance)
        if verbose:
            nodes = len(list(polygons[i].exterior.coords))
            print("Polygon nodes reduced by {:.1f}%, from {} to {}".format(
                100*(nodes_before-nodes)/float(nodes_before),
                nodes_before,
                nodes
                )
            )

def save_svg(full_map, filename='out.svg', stroke_width=1.0, size=500, units="px"):
    size_and_units = "{}{}".format(str(size), units)
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
