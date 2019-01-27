import shapely

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
