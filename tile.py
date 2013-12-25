# -*- coding: utf-8 -*-

import os
import re
from PIL import Image

from fetch import TILE_FOLDER

def stitch_tiles(folder=None):
    """
    The images as downloaded from OpenStreetMap and OpenWeatherMap come in
    256 pixel tiles. This function pastes these back together into a full
    4096 × 4096 image of the earth.
    """
    if not folder:
        # This is to find the latest folder of the form 2013-12-25T11:00:00
        for f in sorted(os.listdir(TILE_FOLDER), reverse=True):
            # ['_earth.png', '_earth', '2013-12-25T11:00:00.png', '2013-12-25T11:00:00', '2013-12-24T12:00:00']
            path = os.path.join(TILE_FOLDER, f)
            if re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', f) and os.path.isdir(path):
                folder = path
                break
    
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
