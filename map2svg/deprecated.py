import pandas as pd

def fetch(list_of_names):
    ox.config(use_cache=True)
    geodataframe = ox.gdf_from_places(list_of_names)
    return geodataframe

def shapefile2polygons_old(sf):
    return [shape(x.shape.__geo_interface__) for x in sf.shapeRecords()]

def proj(geodataframe):
    return ox.project_gdf(geodataframe)

def read_shapefile(shp_path):
    """
    Read a shapefile into a Pandas dataframe with a 'coords' column holding
    the geometry information. This uses the pyshp package
    """
    import shapefile
    #read file, parse out the records and shapes
    sf = shapefile.Reader(shp_path)
    fields = [x[0] for x in sf.fields][1:]
    records = sf.records()
    shps = [s.points for s in sf.shapes()]
    #write into a dataframe
    df = pd.DataFrame(columns=fields, data=records)
    df = df.assign(coords=shps)
    return df

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