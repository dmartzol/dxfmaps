import shapely
from shapely.geometry import shape

class Map(object):
    def __init__(self, sf, continent=None):
        self.sf = sf
        self.continent = continent
        self.polygons = self.shapefile2polygons()
    
    def shapefile2polygons(self):
        if self.continent is None:
            geoms = [self.build_polygon(shapeRecord) for shapeRecord in self.sf.shapeRecords()]
        else:
            geoms = []
            for shapeRecord in self.sf.shapeRecords():
                if shapeRecord.record["CONTINENT"] == self.continent:
                    geoms.append(self.build_polygon(shapeRecord))
        assert len(geoms)>0, "Countries not found"
        return geoms
    
    def build_polygon(self, shapeRecord):
        geom = shape(shapeRecord.shape.__geo_interface__)
        if isinstance(geom, shapely.geometry.polygon.Polygon):
            return geom
        elif isinstance(geom, shapely.geometry.multipolygon.MultiPolygon):
            return self.max_area_polygon(geom)
        else:
            raise Exception('Found non valid geometry')
    
    def max_area_polygon(self, multipolygon):
        # TODO: Try using max and its index
        # index, value = max(list(multipolygon), key=lambda item: item.area)
        p = list(multipolygon)[0]
        for polygon in list(multipolygon):
            if polygon.area > p.area:
                p = polygon
        return p
    
    def filter_by_area(self, area_thresold):
        # TODO: Figure units for area!
        self.polygons = [polygon for polygon in self.polygons if polygon.area > area_thresold]
        assert len(self.polygons) > 0, "We removed too many polygons"
    
    def full_map(self):
        return shapely.geometry.MultiPolygon(polygons)