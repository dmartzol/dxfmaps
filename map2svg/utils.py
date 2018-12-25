import shapely
from shapely.geometry import shape

def list_of_countries(sf):
    name_en = "NAME_EN"
    for x in sf.shapeRecords():
        print("Name: {} ({})".format(x.record[name_en], x.record.oid))

def item_info(sf, n):
    fields = [item[0] for item in sf.fields[1:]]
    record = sf.record(n)
    print("\n Info for item {}\n".format(n))
    for field in fields:
        print("{}: {}".format(field, record[field]))

def project(geodataframe):
    # winkel tripel projection (epsg=54018) 54019
    # {'init': 'epsg:3395'}
    return geodataframe.to_crs({'init': 'epsg:3395'})
    # return geodataframe.to_crs(epsg=54019)

def shapefile2polygons(sf):
    geoms = []
    for item in sf.shapes():
        geom = shape(item.__geo_interface__)
        if isinstance(geom, shapely.geometry.polygon.Polygon):
            geoms.append(geom)
        elif isinstance(geom, shapely.geometry.multipolygon.MultiPolygon):
            geom = max_area_polygon(geom)
        else:
            raise Exception('Found non valid geometry')
        geoms.append(geom)
    return geoms

def max_area_polygon(multipolygon):
    # TODO: Try using max and its index
    # index, value = max(list(multipolygon), key=lambda item: item.area)
    p = list(multipolygon)[0]
    for polygon in list(multipolygon):
        if polygon.area > p.area:
            p = polygon
    return p

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
