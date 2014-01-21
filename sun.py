# -*- coding: utf-8 -*-

import urllib
from datetime import datetime
import os
from math import sin, degrees, radians

# -*- coding: utf-8 -*-

import os
import re
import math
import json
from time import gmtime, strftime

import dateutil.parser
from PIL import Image
import Pysolar

from settings import *


alllatlons = None

try:
    print "Reading in latlon array from file", strftime("%H:%M:%S", gmtime())
    f = open('latitudeslongitudesperpixel.json')
except IOError:
    print "Generating latlon array", strftime("%H:%M:%S", gmtime())
    alllatlons = []
    for x in range(z ** 2 * TILE_SIZE):
        for y in range(z ** 2 * TILE_SIZE):
            alllatlons.append(px2deg(x, y))
    with open('latitudeslongitudesperpixel.json', 'w') as file:
        file.write(json.dumps(alllatlons, indent=2))

if not alllatlons:
    with f:
        alllatlons = json.loads(f.read()) # Maybe there is a more efficient way to read in this 900M file.
print "Done.", strftime("%H:%M:%S", gmtime())

def num2deg(xtile, ytile, zoom=4):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)

def px2deg(x, y, zoom=4):
    xtile = x / 256.0 + 1 / 512.0
    ytile = y / 256.0 + 1 / 512.0
    return num2deg(xtile, ytile, zoom)

def altitude2colors(altitude):
    if 42 > altitude > 0:
        return (255, 255, 0)
    if altitude <= 0:
        return (0, 0, 0)
    else:
        return (255, 255, 255)

def sun(folder=LATEST_PREC_FOLDER):
    """
    This function plots a full 4096 × 4096 image of the earth,
    Pixels are black where it is night and white where it is day.
    
    Where the sun is under 42 degrees of altitude,
    rainbows are possible.
    cf http://www.accuweather.com/en/weather-blogs/weathermatrix/what-is-the-best-time-of-day-for-a-rainbow/32588
    
    This area is yellow.
    """
    
    if not folder:
        print "No folder found."
        return False
    
    DATE = dateutil.parser.parse(LATEST_PREC_SLUG)
    
    full_img = Image.new("RGBA", (z ** 2 * TILE_SIZE, z ** 2 * TILE_SIZE))
    
    print "converting to altitude", strftime("%H:%M:%S", gmtime())
    altitudes = [Pysolar.GetAltitude(latitude, longitude, DATE) for latitude, longitude in alllatlons]
    print "converting to colors", strftime("%H:%M:%S", gmtime())
    colors = map(altitude2colors, altitudes)
    print "drawing to canvas", strftime("%H:%M:%S", gmtime())
    full_img.putdata(colors)
    print "writing to file", strftime("%H:%M:%S", gmtime())
    full_img.save(os.path.join(folder, "%s-sun-rightangle.png" % LATEST_PREC_SLUG))
    print "written", strftime("%H:%M:%S", gmtime())

if __name__ == '__main__':
    sun()
    print "Executed succesfully"

