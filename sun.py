# -*- coding: utf-8 -*-

import os
import json
import subprocess
from time import gmtime, strftime

import dateutil.parser
from PIL import Image
import Pysolar

from settings import *
from geo import *
from utils import logger

alllatlons = None

try:
    logger.debug("Reading in latlon array from file")
    f = open('latitudeslongitudesperpixel.json')
except IOError:
    logger.debug("No file latitudeslongitudesperpixel.json. Generating latlon array")
    alllatlons = []
    for y in range(0, z ** 2 * TILE_SIZE, 8):
        for x in range(0, z ** 2 * TILE_SIZE, 8):
            alllatlons.append(px2deg(x, y))
    logger.debug("Saving latlon array to disk")
    with open('latitudeslongitudesperpixel.json', 'w') as file:
        file.write(json.dumps(alllatlons, indent=2))

if not alllatlons:
    with f:
        alllatlons = json.loads(f.read()) # Maybe there is a more efficient way to read in this 900M file.

def sun(folder=LATEST_PREC_FOLDER):
    """
    This function plots a full 4096 × 4096 image of the earth,
    Pixels are black where it is night and white where it is day.
    
    Where the sun is under 42 degrees of altitude,
    rainbows are possible.
    cf http://www.accuweather.com/en/weather-blogs/weathermatrix/what-is-the-best-time-of-day-for-a-rainbow/32588
    
    This area is yellow.
    """
    def altitude2colors(altitude):
        if 42 > altitude > 0:
            return (255, 255, 255, 0)
        else:
            return (0, 0, 0)
    
    if not folder:
        logger.warn("No latest precipation images folder found, aborting")
        return False
    
    DATE = dateutil.parser.parse(LATEST_PREC_SLUG)
    
    """
    The earth, just for presentation purposes
    """
    background = Image.open(os.path.join(TILE_FOLDER, "_earth.png"))
    
    """
    The mask of where the sun is between 0 and 42 degrees
    We calculate it at a smaller size to be swift
    """
    logger.debug("creating a new image for the sun")
    sun_mask = Image.new("RGBA", (512, 512))
    
    logger.debug("converting to altitude %s points" % len(alllatlons))
    altitudes = [Pysolar.GetAltitudeFast(latitude, longitude, DATE) for latitude, longitude in alllatlons]
    logger.debug("converting to colors")
    colors = map(altitude2colors, altitudes)
    logger.debug("drawing %s colors to canvas" % len(colors))
    sun_mask.putdata(colors)
    
    # Calculate where the sun is in the image
    sun_i = altitudes.index(max(altitudes))
    sun_y = sun_i / 512
    sun_x = sun_i % 512
    sun_mask.putpixel((sun_x, sun_y), (255, 255, 0))
    
    # We’ll need this data for the final image, which is 4096 * 4096, not 512 * 512
    sun_x, sun_y = sun_x * 8, sun_y * 8
    
    logger.debug("rescaling the sun image")
    sun_mask = sun_mask.resize((4096, 4096))
    
    """
    The layer with the satellite imagery
    """
    logger.debug("reading in and resizing the satellite imagery")
    # Figuring out the bounds, in this case via http://oiswww.eumetsat.int/IPPS/html/GE/MET0D_VP-MPE.kml
    # TODO: this is not actually correct
    prec_x, prec_y = deg2px(57.4922, -57.4922)
    prec_x_plus_width, prec_y_plus_height = deg2px(-57.4922, 57.4922)
    prec_width  = prec_x_plus_width  - prec_x
    prec_height = prec_y_plus_height - prec_y
    
    precipitation = Image.open(os.path.join(folder, "GE_MET0D_VP-MPE.png"))
    precipitation.resize((prec_width, prec_height))
    
    logger.debug("convert all the non-transparent pixels to pink points")
    width, _ = precipitation.size
    for i, px in enumerate(precipitation.getdata()):
        if px != (0, 0, 0, 0):
            y = i / width
            x = i % width
            precipitation.putpixel((x, y), (255, 20, 147, 255))
    
    transparent_background = Image.new("RGBA", (4096, 4096))
    transparent_background.paste(precipitation, (prec_x, prec_y), precipitation)
    transparent_background.save(os.path.join(folder, "%s-clouds.png" % LATEST_PREC_SLUG))
    
    """
    Transform the satellite imagery to find rainbows
    """
    logger.debug("call an external imagemagick process to perform a barrel distortion on the clouds")
    infile = os.path.join(folder, "%s-clouds.png" % LATEST_PREC_SLUG)
    outfile = os.path.join(folder, "%s-clouds-bol.png" % LATEST_PREC_SLUG)
    composed_file = os.path.join(folder, "%s-clouds-composed.png" % LATEST_PREC_SLUG)
    barrel_distortion = "0.0 0.0 0.025 0.975 %s %s" % (sun_x, sun_y)
    
    pipe = subprocess.Popen(['convert', infile,
                             '-virtual-pixel', 'gray',
                             '-distort', 'Barrel', barrel_distortion,
                             '-negate',
                             outfile])
    pipe.wait()
    
    pipe = subprocess.Popen(['composite', '-gravity', 'center', outfile, infile, composed_file])
    # convert 2013-12-24T12:00:00Z-clouds.png -virtual-pixel gray -distort Barrel "0.0 0.0 0.05 0.95 2048 2320" -negate 2013-12-24T12:00:00Z-clouds-bol.png
    # mogrify -negate 2013-12-24T12\:00\:00Z-clouds-bol.png
    # composite -gravity center 2013-12-24T12:00:00Z-clouds-bol.png   2013-12-24T12:00:00Z-clouds.png 2013-12-24T12:00:00Z-clouds-composed.png 
    
    cloud_image = Image.open(composed_file)
    
    """
    Bringing it together
    """
    logger.debug("performing imposition for all the images")
    background.paste(cloud_image, (0, 0), cloud_image)
    background.paste(sun_mask, (0, 0), sun_mask)
    
    logger.debug("writing to file")
    background.save(os.path.join(folder, "%s-sun-rightangle.png" % LATEST_PREC_SLUG))
    logger.debug("written")

if __name__ == '__main__':
    sun()
    logger.debug("Executed succesfully")

