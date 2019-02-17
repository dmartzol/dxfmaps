
def shapefile2polygons(sf, continent=None, min_area=None):
    if continent is None:
        geoms = [build_polygon(shapeRecord) for shapeRecord in sf.shapeRecords()]
    else:
        geoms = []
        for shapeRecord in sf.shapeRecords():
            if shapeRecord.record["CONTINENT"] == continent:
                geoms.append(build_polygon(shapeRecord))
    assert len(geoms) > 0, "Countries not found"
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


def filter_by_area(polygons, area_thresold=1000000000):
    # TODO: Figure units for area!
    return [polygon for polygon in polygons if polygon.area > area_thresold]


def fetch(list_of_names):
    ox.config(use_cache=True)
    geodataframe = ox.gdf_from_places(list_of_names)
    return geodataframe


def shapefile2polygons_old2(self):
        if self.continent is None:
            geoms = [self.build_polygon(shapeRecord) for shapeRecord in self.sf.shapeRecords()]
        else:
            geoms = []
            for shapeRecord in self.sf.shapeRecords():
                if shapeRecord.record["CONTINENT"] == self.continent:
                    geoms.append(self.build_polygon(shapeRecord))
        assert len(geoms) > 0, "Countries not found"
        return geoms


def shapefile2polygons_old(sf):
    return [shape(x.shape.__geo_interface__) for x in sf.shapeRecords()]


def proj(geodataframe):
    return ox.project_gdf(geodataframe)


def dataframe2polygons(geodataframe):
    polygons = []
    for _, row in geodataframe.iterrows():
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
