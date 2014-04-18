# -*- coding: utf-8 -*-

"""
Get information from GFS

Cameron Beccario’s https://github.com/cambecc/earth/ explained me how to get GRIB data from the Global Forecast System,
and to convert this into JSON data using his grib2json utility. Something like:

    curl "http://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_hd.pl?file=gfs.t00z.mastergrb2f00&lev_entire_atmosphere_%5C%28considered_as_a_single_layer%5C%29=on&var_PWAT=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgfs.2014022100%2Fmaster" -o "GFS_half_degree.2014022100.grib"    
    grib2json -d -n -o precipitable-water-gfs-0.5.json GFS_half_degree.2014022100.grib

The logic of plotting the data was partly copied from the JavaScript here:
https://github.com/cambecc/earth/blob/e7be4d6810f211217956daf544111502fc57a868/public/libs/earth/1.0.0/products.js#L607

"""

import subprocess
from datetime import datetime
import math
import json
import os

import pytz
import Pysolar
import dateutil.parser
from PIL import Image, ImageOps

from settings import LATEST_GFS_FOLDER, LATEST_GFS_SLUG
from utils import logger

def find_rainclouds():
    if not LATEST_GFS_FOLDER:
        logger.debug("No grib files found. Run fetch.py?")
        return False
    
    DATE = datetime.strptime(LATEST_GFS_SLUG, "%Y%m%d%H")       # strptime can’t handle timezones, what up with that?
    DATE = DATE.replace(tzinfo=pytz.UTC)                        # we know it’s UTC so we add that info http://stackoverflow.com/questions/7065164/how-to-make-an-unaware-datetime-timezone-aware-in-python

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
    
    # the grid's origin (e.g., 0.0E, 90.0N)
    l0 = header['lo1']
    ph0 = header['la1']
    
    # distance between grid points (e.g., 2.5 deg lon, 2.5 deg lat)
    dl = header['dx']
    dph = header['dy']
    
    # number of grid points W-E and N-S (e.g., 144 x 73)
    ni = header['nx']
    nj = header['ny']
    
    logger.debug("read %s points" % len(data))
    logger.debug("the grids origin %sE, %sN" % (l0, ph0))
    logger.debug("distance between grid points: %s deg lon, %s deg lat" % (dl, dph))
    logger.debug("number of grid points W-E: %s, N-S: %s" % (ni, nj))
    
    latitude = ph0
    longitude = l0
    
    altitudes = []
    for j in range(nj):
        for i in range(ni):
            altitudes.append(Pysolar.GetAltitudeFast(latitude, longitude, DATE))
            longitude += dl
        latitude += dph
    
    
    def prec2color(prec):
#        return int(255 - prec * 60) 
        return int(255 - prec * 3)
    
    full_img = Image.new("L", (ni, nj))
    logger.debug("Converting data to color, and writing it to canvas")
    full_img.putdata(map(prec2color, data))
    
    def altitude2colors(altitude):
        if 42 > altitude > 0:
            return 0
        else:
            return 255
    
    sun_mask = Image.new("L", (ni, nj))
    colors = map(altitude2colors, altitudes)
    sun_mask.putdata(colors)
    sun_mask.save('test.png')
    
    full_img.paste(sun_mask, (0, 0), ImageOps.invert(sun_mask))
    
    
    logger.debug("Writing image file")
    full_img.save(png_file_path)
    logger.debug("Written")
    

if __name__ == '__main__':
    find_rainclouds()

