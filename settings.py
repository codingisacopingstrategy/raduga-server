import os
import re
import sys
from glob import glob

"""
WEATHER RESOURCES SETTINGS
"""

ZOOM_LEVEL = z =  4
TILE_SIZE = 256

TILE_SERVER        = "http://{s}.tile.openweathermap.org/map/precipitation_cls/{z}/{x}/{y}.png"
TILE_FOLDER        = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'raduga_tiles')
GFS_FOLDER         = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'gfs')
ELEKTRO_L_FOLDER         = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'elektro')

def get_latest_prec_folder():
    """
    This is to find the latest folder of the form 2013-12-25T11:00:00
    """
    global TILE_FOLDER
    for f in sorted(os.listdir(TILE_FOLDER), reverse=True):
        # ['_earth.png', '_earth', '2013-12-25T11:00:00.png', '2013-12-25T11:00:00', '2013-12-24T12:00:00']
        slug = f
        path = os.path.join(TILE_FOLDER, f)
        if re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', slug) and os.path.isdir(path):
            return path, slug

# This is to find the latest folder of the form 2014022100
def get_latest_gfs_folder():
    global GFS_FOLDER
    for f in sorted(os.listdir(GFS_FOLDER), reverse=True):
        slug = f
        path = os.path.join(GFS_FOLDER, slug)
        if re.match(r'\d{10}', slug) and os.path.isdir(path) and len(glob(os.path.join(path, '*pwat.grib'))) > 0:
            return path, slug

def get_latest_rainbows_url():
    slug = get_latest_gfs_folder()[1]
    return "/static/gfs/" + slug + "/rainbows." + slug + ".json"

def get_latest_elektro_l_url():
    global ELEKTRO_L_FOLDER
    for f in sorted(os.listdir(ELEKTRO_L_FOLDER), reverse=True):
        return "/static/elektro/" + f

LATEST_PREC_FOLDER, LATEST_PREC_SLUG = get_latest_prec_folder()
LATEST_GFS_FOLDER, LATEST_GFS_SLUG   = get_latest_gfs_folder()

