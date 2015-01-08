# -*- coding: utf-8 -*-

# Python Standard Library 
import os
from datetime import datetime

# Dependencies: Flask + PIL or Pillow
from flask import Flask, send_from_directory, redirect as redirect_flask, render_template
import pymongo

# Local imports
from settings import *

app = Flask(__name__)

client = pymongo.MongoClient()
db = client.raduga

# Redirects should not be cached by the devices:
def redirect(uri):
    """
    http://arusahni.net/blog/2014/03/flask-nocache.html
    """
    response = redirect_flask(uri)
    response.headers['Last-Modified'] = datetime.now()
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# These static files should be served by the web server
@app.route('/tiles/<path:filename>')
def base_static(filename):
    return send_from_directory(os.path.join(app.root_path, 'raduga_tiles'), filename)

@app.route('/')
def readme():
    return send_from_directory(app.root_path, 'README.md')

# Note: this will always serve the same file
# Should be used in collaboration with nginx, that is, with a try -f
# block: nginx tries to find an actual elektro l image for the
# provided time-slug; if it doesn’t exist flask will redirect to the
# `error` image. Come to think of it, nginx could do this too!
@app.route('/static/elektro/<time_slug>_RGB.png')
def elektro_fallback(time_slug):
    return redirect('/static/elektro/130502_0030_10.png')

@app.route("/latest/elektro-l")
def latest_elektro():
    return redirect(get_latest_elektro_l_url())

@app.route("/latest/rainbows.json")
def latest_rainbows():
    return redirect(get_latest_rainbows_url())

@app.route("/latest/clouds.json")
def latest_clouds():
    return redirect(get_latest_clouds_url())

@app.route("/latest/rainbow_cities.json")
def latest_rainbow_cities():
    return redirect(get_latest_rainbow_cities_url())

@app.route("/hq/")
def hq():
    logs = db.log.find().sort("$natural", pymongo.DESCENDING)
    forecasts = get_forecast_info()
    return render_template("hq.html", logs=logs, forecasts=forecasts)

if __name__ == '__main__':
    app.run(debug=True)
