from dxfmaps.map import Map
from dxfmaps.projections import MERCATOR, WINKEL_TRIPEL
import sys

TOLERANCE = 0.05
AREA_LIMIT = 2.0


def main():
    countries = [
        'afghanistan',
        'albania',
        'algeria',
        'angola',
        'antarctica',
        'argentina',
        'armenia',
        'australia',
        'austria',
        'azerbaijan',
        'bangladesh',
        'belarus',
        'belgium',
        'benin',
        'bhutan',
        'bolivia',
        'bosnia and herz.',
        'botswana',
        'brazil',
        'bulgaria',
        'burkina faso',
        'burundi',
        'cambodia',
        'cameroon',
        'canada',
        'central african rep.',
        'chad',
        'chile',
        'china',
        'colombia',
        'congo',
        'costa rica',
        'croatia',
        'cuba',
        'czechia',
        "côte d'ivoire",
        'dem. rep. congo',
        'denmark',
        'dominican rep.',
        'ecuador',
        'egypt',
        'eq. guinea',
        'eritrea',
        'estonia',
        'ethiopia',
        'finland',
        'france',
        'gabon',
        'georgia',
        'germany',
        'ghana',
        'greece',
        'greenland',
        'guatemala',
        'guinea',
        'guinea-bissau',
        'guyana',
        'haiti',
        'honduras',
        'hungary',
        'iceland',
        'india',
        'indonesia',
        'iran',
        'iraq',
        'ireland',
        'israel',
        'italy',
        'japan',
        'jordan',
        'kazakhstan',
        'kenya',
        'kyrgyzstan',
        'laos',
        'latvia',
        'lesotho',
        'liberia',
        'libya',
        'lithuania',
        'macedonia',
        'madagascar',
        'malawi',
        'malaysia',
        'mali',
        'mauritania',
        'mexico',
        'moldova',
        'mongolia',
        'morocco',
        'mozambique',
        'myanmar',
        'namibia',
        'nepal',
        'netherlands',
        'new zealand',
        'nicaragua',
        'niger',
        'nigeria',
        'north korea',
        'norway',
        'oman',
        'pakistan',
        'panama',
        'papua new guinea',
        'paraguay',
        'peru',
        'philippines',
        'poland',
        'portugal',
        'romania',
        'russia',
        'rwanda',
        's. sudan',
        'saudi arabia',
        'senegal',
        'serbia',
        'sierra leone',
        'slovakia',
        'slovenia',
        'somalia',
        'somaliland',
        'south africa',
        'south korea',
        'spain',
        'sri lanka',
        'sudan',
        'suriname',
        'sweden',
        'switzerland',
        'syria',
        'taiwan',
        'tajikistan',
        'tanzania',
        'thailand',
        'togo',
        'tunisia',
        'turkey',
        'turkmenistan',
        'uganda',
        'ukraine',
        'united arab emirates',
        'united kingdom',
        'united states of america',
        'uruguay',
        'uzbekistan',
        'venezuela',
        'vietnam',
        'w. sahara',
        'yemen',
        'zambia',
        'zimbabwe'
    ]

    shp_path = sys.argv[1]
    map = Map(shp_path, countries_set=set(countries))
    map.filter_by_area(area_limit=AREA_LIMIT)
    map.simplify(tolerance=TOLERANCE)
    map.info()
    # map.project(WINKEL_TRIPEL)
    map.project(MERCATOR)
    map.translate_to_center()
    map.scale_to_width(2000)
    print(map.bounds)
    scaling_factor = map.scaling_factor
    map.to_dxf(filename='world.dxf')
    map.to_png(filename='world.png', white_bg=True)

    # for country in countries:
    #     print(country)
    #     country_set = set([country])
    #     map_by_pieces = Map(shp_path, countries_set=country_set)
    #     map_by_pieces.filter_by_area(area_limit=AREA_LIMIT)
    #     map_by_pieces.simplify(tolerance=TOLERANCE)
    #     map_by_pieces.project(WINKEL_TRIPEL)
    #     map_by_pieces.translate_to_center()
    #     map_by_pieces.scale(scaling_factor)
    #     map_by_pieces.add_labels(n=15, fast=True)
    #     map_by_pieces.to_svg(filename=country + '.svg', stroke=0.2)
    #     map_by_pieces.to_png(filename=country + '.png', stroke=0.2)
    #     map_by_pieces.to_dxf(filename=country + '.dxf')
    #     break


if __name__ == "__main__":
    main()
