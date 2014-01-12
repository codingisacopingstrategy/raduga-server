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
from tile import stitch_tiles

#
def deg2px(lat_deg, lon_deg, zoom=4):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom * 256
    xpx = int((lon_deg + 180.0) / 360.0 * n)
    ypx = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xpx, ypx)

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
