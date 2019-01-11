import shapely
from shapely.geometry import shape

def shapefile2polygons(sf, continent=None, min_area=None):
    if continent is None:
        geoms = [build_polygon(shapeRecord) for shapeRecord in sf.shapeRecords()]
    else:
        geoms = []
        for shapeRecord in sf.shapeRecords():
            if shapeRecord.record["CONTINENT"] == continent:
                geoms.append(build_polygon(shapeRecord))
    assert len(geoms)>0, "Countries not found"
    return geoms

def build_polygon(shapeRecord):
    geom = shape(shapeRecord.shape.__geo_interface__)
    if isinstance(geom, shapely.geometry.polygon.Polygon):
        return geom
    elif isinstance(geom, shapely.geometry.multipolygon.MultiPolygon):
        return max_area_polygon(geom)
    else:
        raise Exception('Found non valid geometry')

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

def project(geodataframe):
    # winkel tripel projection (epsg=54018) 54019
    # {'init': 'epsg:3395'}
    return geodataframe.to_crs({'init': 'epsg:3395'})
    # return geodataframe.to_crs(epsg=54019)

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
