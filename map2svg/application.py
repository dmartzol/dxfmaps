from map2svg import names
import osmnx as ox
import shapely

def main():
    ox.config(use_cache=True)
    comunidades_gdf = ox.gdf_from_places(names.CCAA)
    for index, row in comunidades_gdf.iterrows():
        if isinstance(row.geometry, shapely.geometry.multipolygon.MultiPolygon):
            multipolygon = row.geometry
            areas = [poligon.area for poligon in multipolygon.geoms]
            maximum_area = max(areas)
            max_area_polygon = row.geometry.geoms[areas.index(maximum_area)]
            comunidades_gdf.iloc[index,4] = max_area_polygon
    # project the geometry to the appropriate UTM zone
    comunidades_gdf = ox.project_gdf(comunidades_gdf)
    polygons = []
    for index, row in comunidades_gdf.iterrows():
        polygons.append(row.geometry)
