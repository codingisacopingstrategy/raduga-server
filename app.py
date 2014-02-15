# -*- coding: utf-8 -*-

# Python Standard Library 
import os
import re
import sys
import math
import fnmatch

# Dependencies: Flask + PIL or Pillow
from flask import Flask, send_from_directory, render_template, jsonify, request
from PIL import Image

# Local imports
from geo import deg2px
from tile import stitch_tiles
from settings import *


def update_img():
    global LATEST_PREC_FOLDER, LATEST_PREC_SLUG, LATEST_PREC_IMG_PATH, LATEST_PREC_IMG
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

app = Flask(__name__)

# These static files should be served by the web server
@app.route('/tiles/<path:filename>')
def base_static(filename):
    return send_from_directory(os.path.join(app.root_path, 'raduga_tiles'), filename)

@app.route("/test/as_map")
def pre_vis_tiled():
    return render_template('map.html', LATEST_PREC_SLUG=LATEST_PREC_SLUG)

@app.route("/test/as_image")
def pre_vis_stitched():
    return render_template('image.html', LATEST_PREC_SLUG=LATEST_PREC_SLUG)
 
@app.route("/chance", methods=['POST',])
def rainbow_chance():
    latitude = request.json['latitude']
    longitude = request.json['longitude']
    print LATEST_PREC_IMG.getpixel(deg2px(latitude, longitude))
    obj = {
       'latitude' : latitude,
       'longitude' : longitude
      }
    return jsonify(obj)

if __name__ == '__main__':
    app.run(debug=True)
