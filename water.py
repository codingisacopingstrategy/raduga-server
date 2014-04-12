# -*- coding: utf-8 -*-

"""
Get information from GFS

Cameron Beccario’s https://github.com/cambecc/earth/ explained me how to get GRIB data from the Global Forecast System,
and to convert this into JSON data using his grib2json utility. Something like:

    curl "http://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_hd.pl?file=gfs.t00z.mastergrb2f00&lev_entire_atmosphere_%5C%28considered_as_a_single_layer%5C%29=on&var_PWAT=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgfs.2014022100%2Fmaster" -o "GFS_half_degree.2014022100.grib"    
    grib2json -d -n -o precipitable-water-gfs-0.5.json GFS_half_degree.2014022100.grib

For some pointers on how to then plot this data, see:
https://github.com/cambecc/earth/blob/e7be4d6810f211217956daf544111502fc57a868/public/libs/earth/1.0.0/products.js#L607

"""

import subprocess
import json
import os

import dateutil.parser
from PIL import Image

from settings import LATEST_GFS_FOLDER, LATEST_GFS_SLUG
from utils import logger

def find_rainclouds():
    if not LATEST_GFS_FOLDER:
        logger.debug("No grib files found. Run fetch.py?")
        return False
    grib_file_path = os.path.join(LATEST_GFS_FOLDER, "GFS_half_degree.%s.pwat.grib" % LATEST_GFS_SLUG)
    json_file_path = os.path.join(LATEST_GFS_FOLDER, "GFS_half_degree.%s.pwat.json" % LATEST_GFS_SLUG)
    png_file_path = os.path.join(LATEST_GFS_FOLDER, "GFS_half_degree.%s.pwat.png" % LATEST_GFS_SLUG)
    
    if not os.path.exists(grib_file_path):
        logger.debug("Expected GRIB file not foud")
        return False
    if os.path.exists(json_file_path):
        logger.debug("Corresponding JSON found, skipping JSON conversion")
    else:
        logger.debug("Converting GRIB into JSON file: %s" % json_file_path)
        pipe = subprocess.Popen(['grib2json', '-d', '-n',
                             '-o', json_file_path,
                             grib_file_path])
        pipe.wait()
        
    with open(json_file_path) as f:
        j = json.loads(f.read())
    
    header = j[0]['header']
    data   = j[0]['data']
    
    # number of grid points W-E and N-S (e.g., 144 x 73)
    ni = header['nx']
    nj = header['ny']
    
    def prec2color(prec):
#        return int(255 - prec * 60) 
        return int(255 - prec * 3)
    
    full_img = Image.new("L", (ni, nj))
    logger.debug("Converting data to color, and writing it to canvas")
    full_img.putdata(map(prec2color, data))
    logger.debug("Writing image file")
    full_img.save(png_file_path)
    logger.debug("Written")
    

if __name__ == '__main__':
    find_rainclouds()

