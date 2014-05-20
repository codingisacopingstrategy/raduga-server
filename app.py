# -*- coding: utf-8 -*-

# Python Standard Library 
import os

# Dependencies: Flask + PIL or Pillow
from flask import Flask, send_from_directory, redirect, render_template
from pymongo import MongoClient

# Local imports
from settings import *

app = Flask(__name__)

client = MongoClient()
db = client.photos

# These static files should be served by the web server
@app.route('/tiles/<path:filename>')
def base_static(filename):
    return send_from_directory(os.path.join(app.root_path, 'raduga_tiles'), filename)

@app.route('/')
def readme():
    return send_from_directory(app.root_path, 'README.txt')

@app.route("/latest/elektro-l")
def latest_elektro():
    return redirect(get_latest_elektro_l_url())

@app.route("/latest/rainbows.json")
def latest_rainbows():
    return redirect(get_latest_rainbows_url())

@app.route("/latest/clouds.json")
def latest_clouds():
    return redirect(get_latest_clouds_url())

@app.route("/hq/")
def hq():
    logs = db.log.find()
    return render_template("hq.html", logs=logs)

if __name__ == '__main__':
    app.run(debug=True)
