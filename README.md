# dxfmaps (Work In Progress)

Python module to generate vector maps from ESRI Shapefiles with the purpose of cutting custom maps in CNC controlled machines(e.g. Laser cutters or CNC milling machines).

![Example](https://github.com/dmartzol/dmartzol.github.io/raw/master/images/europe/europe.png)

## Features

- [X] Convenient SVG and DXF formats to import into CNC software for processing and cut.
- [X] Specify the desired width or height of the final SVG/DXF.
- [X] Generate a vector map of all countries in a continent by just specifying the name of the continent.
- [X] Reducing the number of points in the data by simplifying polygons.
- [ ] Generate a map of all the provinces/states in a country specifying the name of the country.

## Installation

Install with:

```Bash
git clone https://github.com/dmartzol/dxfmaps.git
cd dxfmaps
pip install -e .
```


### Requirements

* [pyshp](https://github.com/GeospatialPython/pyshp) - Library for reading ESRI Shapefiles
* [Shapely](https://github.com/Toblerity/Shapely) - Manipulation and analysis of geometric objects
* [ezdxf](https://github.com/mozman/ezdxf) - Creation and manipulation of DXF drawings

## Usage and examples

```Python
import dxfmaps

def main():
    sf = shapefile.Reader(dxfmaps.utils.WORLD_COUNTRIES)
    map = dxfmaps.map.Map(sf, continent="europe")
    map.filter_by_area(area_thresold = .5)
    map.project('mercator')
    map.simplify(tolerance=.05)
    map.translate_to_center()
    map.scale_width()
    map.to_svg(filename='europe.svg')
    map.to_dxf()

if __name__ == '__main__':
    main()
```

## TO DO

- [X] Implement Azimuthal and Winkel Triple and Mercator projections.
- [X] Implement smaller buffered map for back support.
- [X] Add country names.
- [ ] Implement PNG support.
- [ ] Implement maximum rectangle in polygon
- [ ] Update this README.
- [ ] Include shapefile reader into the module.
- [ ] Add credits(Natural Earth logo, etc).
- [ ] Replace asserts for exceptions/errors (correctly).
- [ ] Comment code.
- [ ] Implement scale as ratio for Azimuthal equidistant projection.
- [ ] Implement verbose mode (correctly).
- [ ] Add support for other data sources(.gov)
- [ ] Calculate adequate tolerance for method 'simplify'.
- [ ] Implement imperial units?
- [ ] Try preserve_topology=False in simplify func


## License

This project is licensed under the MIT License

## Acknowledgments

*  Built using data from Natural Earth, using the maps for countries and states/provinces.
