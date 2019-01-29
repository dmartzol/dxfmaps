# dxfmaps (Work In Progress)

Python module to generate vector maps from ESRI Shapefiles with the purpose of cutting custom maps in CNC controlled machines(e.g. Laser cutters or CNC milling machines).

![Example](https://github.com/dmartzol/dmartzol.github.io/raw/master/images/europe/europe.png)

## Features

- [X] Convenient SVG and DXF formats to import into CNC software for processing and cut.
- [X] Specify the desired width of the final SVG/DXF.
- [X] Generate a vector map of all countries in a continent by just specifying the name of the continent.
- [X] Generate a map reducing the number of points in it by simplifying polygons.
- [ ] Generate a map of all the provinces/states in a country specifying the name of the country.

## Installation

Install with:

```
git clone https://github.com/dmartzol/dxfmaps.git
cd dxfmaps
pip install -e .
```


### Requirements

* [pyshp](https://github.com/GeospatialPython/pyshp) - Library for reading ESRI Shapefiles
* [Shapely](https://github.com/Toblerity/Shapely) - Manipulation and analysis of geometric objects
* [ezdxf](https://github.com/mozman/ezdxf) - Creation and manipulation of DXF drawings

## Usage and examples
```python
import dxfmaps

def main():
    map = dxfmaps.Map('shapefile.shp', continent='europe')
    map.filter_by_area(area_thresold = .5)
    map.simplify(tolerance=.05)
    map.translate_to_center()
    map.scale()
    map.to_svg()

if __name__ == '__main__':
    main()
```

## TO DO

- [ ] Fix scale
- [ ] Include shapefile reader into the module
- [ ] Change name of output buffered file
- [ ] Implemente verbose mode (correctly)
- [ ] Implement different projections.
- [ ] Implement imperial units.
- [ ] Add credits(Natural Earth logo, etc)
- [ ] Add support for other sources(.gov)
- [ ] Add country names
- [ ] Replace asserts for exceptions/errors
- [ ] Calculate adequate tolerance for method 'simplify'



## License

This project is licensed under the MIT License

## Acknowledgments

*  Built using data from Natural Earth, using the maps for countries and states/provinces.
