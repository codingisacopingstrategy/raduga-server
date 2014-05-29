# -*- coding: utf-8 -*-
"""
Check which cities are in one of the rainbow_areas as predicted in water.py
"""
import json
import codecs

from PIL import Image

from settings import *
from geo import position_to_point
from utils import logger

def find_rainbow_cities(GFS_SLUG):
    logger.debug("loading list of cities")
    cities = json.loads(open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "scrape", "cities.json")).read())
    
    logger.debug("loading specified rainbow analysis image")
    CURRENT_GFS_FOLDER = os.path.join(GFS_FOLDER, GFS_SLUG)
    rainbow_analysis_image_path = os.path.join(CURRENT_GFS_FOLDER, "GFS_half_degree.%s.pwat.png" % GFS_SLUG)
    try:
        image = Image.open(rainbow_analysis_image_path)
    except IOError:
        logger.error("did not find image file")
        return False
    
    access = image.load()
    
    rainbow_cities_json_path = os.path.join(CURRENT_GFS_FOLDER, "%s.rainbow_cities.json" % GFS_SLUG)
    
    rainbow_cities = []
    
    logger.debug("checking each city against rainbow analysis")
    
    for city in cities:
        # position_to_point allows to translate a geographic coordinate into a pixel value
        # for the image we produced from the gfs data
        point = position_to_point((city['lon'], city['lat']))
        # there are black pixels where we predict rainbows
        if access[point[0], point[1]] == 0:
            rainbow_cities.append(city)
    
    if len(rainbow_cities) > 0:
        logger.debug(
                     (u"found rainbow cities: %s" % u', '.join(city['name_ru'] + '/' + city['name_en'] for city in rainbow_cities)).encode('utf8')
                     )
    else:
        logger.debug("no rainbow cities found")
    
    with codecs.open(rainbow_cities_json_path, 'w', 'utf-8') as f:
        f.write(json.dumps(rainbow_cities, indent=4, ensure_ascii=False))

if __name__ == '__main__':
    logger.debug('looking for rainbow-forecasts for which to find cities')
    for f in sorted(os.listdir(GFS_FOLDER), reverse=True):
        slug = f
        path = os.path.join(GFS_FOLDER, slug)
        if re.match(r'\d{10}', slug) and os.path.isdir(path):
            if len(glob(os.path.join(path, '*rainbow_cities.json'))) > 0:
                logger.debug("encountered already processed rainbow-forecast %s, stop searching for rainbow-forecasts" % slug)
                break
            if len(glob(os.path.join(path, '*pwat.grib'))) > 0:
                logger.debug("encountered cityless rainbow-forecast %s, start processing" % slug)
                find_rainbow_cities(slug)
