# -*- coding: utf-8 -*-

import urllib
from datetime import datetime
import os

TILE_SERVER = "http://{s}.tile.openweathermap.org/map/precipitation_cls/{z}/{x}/{y}.png"
TILE_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'raduga_tiles')

 
class AppURLopener(urllib.FancyURLopener):
    version = 'Mozilla/5.0'
 
urllib._urlopener = AppURLopener()

def quantisised_time():
    """
    ISO representation of datetime rounded to nearest hour.
    To use for folder names etcetera.
    """
    return datetime.now().strftime("%Y-%m-%dT%H:00:00Z")

def fetch():
    """
    Download the latest precipitation tiles.
    At zoom level 4, there are 4² × 4² = 16 × 16 = 256 tiles.
    """
    ZOOM_LEVEL = z =  4
    
    for x in range(z ** 2):
        for y in range(z ** 2):
            uri = TILE_SERVER.format(s='a', z=z, x=x, y=y)
            # make a folder like raduga_tiles/4/5/
            path = os.path.join(TILE_FOLDER, quantisised_time(), str(z), str(x))
            if not os.path.exists(path):
                os.makedirs(path)
            output_file = os.path.join(path, '%s.png' % y)
            urllib.urlretrieve(uri, output_file)

if __name__ == '__main__':
    fetch()
