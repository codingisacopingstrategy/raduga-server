# -*- coding: utf-8 -*-

# Python Standard Library 
import os
import re
import sys
import fnmatch

# Dependencies: Flask + PIL or Pillow
from flask import Flask, send_from_directory, render_template, jsonify, request
from PIL import Image

# Local imports
from tile import stitch_tiles

# Constants
TILE_SERVER        = "http://{s}.tile.openweathermap.org/map/precipitation_cls/{z}/{x}/{y}.png"
TILE_FOLDER        = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'raduga_tiles')

LATEST_PREC_FOLDER   = None
LATEST_PREC_SLUG     = None
LATEST_PREC_IMG_PATH = None
LATEST_PREC_IMG      = None

def update_img():
    global LATEST_PREC_FOLDER, LATEST_PREC_SLUG, LATEST_PREC_IMG_PATH, LATEST_PREC_IMG
    # Check what is the latest downloaded precipitation map
    for f in sorted(os.listdir(TILE_FOLDER), reverse=True):
    # ['_earth.png', '_earth', '2013-12-25T11:00:00.png', '2013-12-25T11:00:00', '2013-12-24T12:00:00']
        slug = f
        path = os.path.join(TILE_FOLDER, f)
        if re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', slug) and os.path.isdir(path):
            LATEST_PREC_FOLDER = path
            LATEST_PREC_SLUG = slug
            break
    # Check if we have found image tiles
    if not LATEST_PREC_FOLDER:
        sys.exit("No tiles found")
    # Check if the stitched image is already present 
    LATEST_PREC_IMG_PATH = os.path.join(TILE_FOLDER, u'%s.png' % slug)
    if not os.path.exists(LATEST_PREC_IMG_PATH):
        # If not, stitch it
        print "Stitching tiles in for %s" % LATEST_PREC_SLUG
        stitch_tiles(LATEST_PREC_FOLDER) 
    return Image.open(LATEST_PREC_IMG_PATH)

LATEST_PREC_IMG = update_img()

app = Flask(__name__, static_folder='raduga_tiles', static_url_path='/tiles')

@app.route("/test/as_map")
def pre_vis_tiled():
    return render_template('map.html', LATEST_PREC_SLUG=LATEST_PREC_SLUG)

@app.route("/test/as_image")
def pre_vis_stitched():
    return render_template('image.html', LATEST_PREC_SLUG=LATEST_PREC_SLUG)

if __name__ == '__main__':
    app.run(debug=True)
