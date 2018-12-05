from map2svg import names
from map2svg.utils import project, filter_by_area, dataframe2polygons, simplify, save_svg
import osmnx as ox
import shapely
import geopandas as gpd
import os


def main():
    f = os.path.join("shapefiles", "cb_2017_us_state_500k", "cb_2017_us_state_500k.shp")
    shapefile = gpd.read_file(f)
    for i, row in shapefile.iterrows():
        if row.NAME not in names.USA_STATES:
            shapefile.drop(index = i, inplace = True)
    states_gdf_projection = project(shapefile)
    polygons = dataframe2polygons(states_gdf_projection)

    print("States in list: {}".format(len(names.USA_STATES)))
    print("Polygons before filtering by area: {}".format(len(polygons)))
    polygons = filter_by_area(polygons, area_thresold = 1000000000)
    print("Polygons after filtering by area: {}".format(len(polygons)))
    
    simplify(polygons, tolerance = 5000)

    # Translating the map to the origin
    full_map = shapely.geometry.MultiPolygon(polygons)
    offset_x = - min(full_map.bounds[0], full_map.bounds[2])
    offset_y = - min(full_map.bounds[1], full_map.bounds[3])
    full_map = shapely.affinity.translate(full_map, xoff=offset_x, yoff=offset_y)

    # Scaling the polygons to reduce their size
    factor = 90 / max(full_map.bounds)
    factor = 1.91787670701e-05
    print("")
    print("Scaling factor: {}".format(factor))
    print("Old bounds: {}".format(full_map.bounds))
    full_map = shapely.affinity.scale(full_map, xfact=factor, yfact=factor, origin=(0, 0))
    print("New bounds: {}".format(full_map.bounds))

    save_svg(full_map, size="500", units="px")
    interior = full_map.buffer(0.5, cap_style=2, join_style=1)
    interior = interior.buffer(-1.0, cap_style=2, join_style=1)
    save_svg(interior, filename='out_buffered.svg', size="500", units="px")
