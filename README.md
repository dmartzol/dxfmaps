# dxfmaps (Work In Progress)

Python module to generate vector maps from ESRI Shapefiles with the purpose of cutting custom maps in CNC controlled machines(e.g. Laser cutters or CNC milling machines).

![Example](https://github.com/dmartzol/dmartzol.github.io/raw/master/images/europe/europe.png)

## Features

- [X] Convenient SVG and DXF formats to import into CNC software for processing and cut.
- [X] Specify the desired width or height of the final SVG/DXF.
- [X] Include label for each country in separate layers of the DXF file.
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
from dxfmaps.map import Map
from dxfmaps.utils import WORLD_COUNTRIES
from dxfmaps.projections import *


def main():
    map = Map(WORLD_COUNTRIES, continent="europe")
    map.filter_by_area(area_limit=1.0)
    map.simplify(tolerance=.015)
    map.project(MERCATOR)
    map.translate_to_center()
    map.scale_to_width(1000)
    map.add_labels()
    map.to_png(filename='europe.png', stroke_width=2.0)
    map.to_svg()
    map.to_dxf()


if __name__ == "__main__":
    main()
```

## TO DO

- [X] Implement Azimuthal and Winkel Triple and Mercator projections.
- [X] Implement smaller buffered map for back support.
- [X] Add country names.
- [X] Implement PNG support.
- [ ] Implement maximum rectangle in polygon
- [ ] Include shapefile reader into the module.
- [ ] Add credits(Natural Earth logo, etc).
- [ ] Comment code.
- [ ] Add support for other data sources(.gov)
- [ ] Calculate adequate tolerance for method 'simplify'.
- [ ] Implement imperial units?


## License

This project is licensed under the MIT License

## Acknowledgments

*  Built using data from Natural Earth, using the maps for countries and states/provinces.
