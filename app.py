# -*- coding: utf-8 -*-

# Python Standard Library 
import os

# Dependencies: Flask + PIL or Pillow
from flask import Flask, send_from_directory

# Local imports
from settings import *

app = Flask(__name__)

# These static files should be served by the web server
@app.route('/tiles/<path:filename>')
def base_static(filename):
    return send_from_directory(os.path.join(app.root_path, 'raduga_tiles'), filename)


if __name__ == '__main__':
    app.run(debug=True)
