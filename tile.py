# -*- coding: utf-8 -*-

import os
import re

from PIL import Image

from settings import TILE_SERVER, TILE_FOLDER, LATEST_PREC_FOLDER

def stitch_tiles(folder=LATEST_PREC_FOLDER):
    """
    The images as downloaded from OpenStreetMap and OpenWeatherMap come in
    256 pixel tiles. This function pastes these back together into a full
    4096 × 4096 image of the earth.
    """
    
    if not folder:
        print "No folder found."
        return False
    
    ZOOM_LEVEL = z =  4
    TILE_SIZE = 256
    
    full_img = Image.new("RGBA", (z ** 2 * TILE_SIZE, z ** 2 * TILE_SIZE))
    
    for x in range(z ** 2):
        for y in range(z ** 2):
            img_path = os.path.join(TILE_FOLDER, folder, str(z), str(x), '%s.png' % y)
            img = Image.open(img_path)
            full_img.paste(img, (x * TILE_SIZE, y * TILE_SIZE))
    
    full_img.save(os.path.join(TILE_FOLDER, "%s.png" % folder))

if __name__ == '__main__':
    stitch_tiles()
