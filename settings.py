import os
import re

TILE_SERVER        = "http://{s}.tile.openweathermap.org/map/precipitation_cls/{z}/{x}/{y}.png"
TILE_FOLDER        = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'raduga_tiles')

LATEST_PREC_FOLDER = None
LATEST_PREC_SLUG   = None
LATEST_PREC_IMG    = None

# This is to find the latest folder of the form 2013-12-25T11:00:00
for f in sorted(os.listdir(TILE_FOLDER), reverse=True):
    # ['_earth.png', '_earth', '2013-12-25T11:00:00.png', '2013-12-25T11:00:00', '2013-12-24T12:00:00']
    slug = f
    path = os.path.join(TILE_FOLDER, f)
    if re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', slug) and os.path.isdir(path):
        LATEST_PREC_FOLDER = path
        LATEST_PREC_SLUG = slug
        break

