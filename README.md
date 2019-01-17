# map2DXF
-

## This README is work in progress, some of the examples here don't work yet.

Python module to generate vector maps from ESRI Shapefiles with the purpose of cutting custom maps in CNC controlled machines(e.g. Laser cutters or CNC milling machines).

![Example](https://github.com/dmartzol/dmartzol.github.io/raw/master/images/europe/europe.png)

## Features

- [ ] Convenient SVG and <del>DXF</del> formats to import into CNC software for processing and cut.
- [ ] Specify the desired width of the final SVG/DXF.
- [x] Generate a vector map of all countries in a continent by just specifying the name of the continent.
- [x] Generate a map reducing the number of points in it by simplifying polygons.
- [ ] <del>Generate a map of all the provinces/states in a country specifying the name of the country.</del>

## Installation

Install with:

```
git clone https://github.com/dmartzol/map2svg.git
cd map2SVG
pip install -e .
```


### Requirements

* [pyshp](https://github.com/GeospatialPython/pyshp) - Library for reading ESRI Shapefiles
* [Shapely](https://github.com/Toblerity/Shapely) - Manipulation and analysis of geometric objects

## Usage and examples
```python
import map2svg

def main():
    map = map2svg.Map('shapefile.shp', continent='europe')
    map.filter_by_area(area_thresold = .5)
    map.simplify(tolerance=.05)
    map.translate_to_center()
    map.scale()
    map.to_svg()

if __name__ == '__main__':
    main()
```

## TO DO
- [ ] Implement actual DXF format(Curently only SVG is supported).
- [ ] Implement different projections.
- [ ] Credit Natural Earth data.
- [ ] SVG to DXF
- [ ] Add credits(Natural Earth logo, etc)
- [ ] Add support for other sources(.gov)

## License

This project is licensed under the MIT License

## Acknowledgments

* Made with data from Natural Earth, using the maps for countries or states/provinces.