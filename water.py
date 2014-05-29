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
from glob import glob
import math
import json
import sys
import os
import re

import pytz
import Pysolar
import dateutil.parser
from PIL import Image, ImageOps, ImageFilter, ImageEnhance

from settings import GFS_FOLDER, LATEST_GFS_SLUG
from utils import logger


def img2features(image, colours=False):
    """
    colours=False:
    Given a grey-scale image, return a Geo-JSON string, that for each black pixel
    represents a square point on the map.
    
    colours=True:
    Given a grey-scale image, return a Geo-JSON string, that for each grey pixel
    represents a square point on the map, with the grey colour as a property.
    """
    
    rainbow_colours = [[255, 0, 0], [255, 127, 0], [255, 255, 0], [0, 255, 0], [0, 0, 255], [75, 0, 130], [143, 0, 255]]
    
    def blend_colours(colour_1, colour_2, percentage):
        new_colour =[]
        for i in range(3):
            new_colour.append( int( colour_1[i] + (colour_2[i] - colour_1[i]) * percentage * .01 ) )
        return "rgb(" + ', '.join(map(str, new_colour)) + ")"
    
    
    def gradient_stops(lon):
        """
        rainbow value inbetween 0, 700
        corresponds to lon 25, 192
        """
        
        index =  (int(lon) - 25) * 4
    
        start_colour  = rainbow_colours[index / 100]
        end_colour    = rainbow_colours[(index / 100) + 1]
    
        percentage_start = index % 100
        percentage_stop  = percentage_start + 2
    
        return( blend_colours(start_colour, end_colour, percentage_start), blend_colours(start_colour, end_colour, percentage_stop) )
    
    def px2feature(px, colour=None):
        left    = px[0] * .5
        right   = left + 0.5
        top     = px[1] * -.5 + 90
        bottom  = top - 0.5
        feature =  {   "type": "Feature",
                    "geometry": { "type": "Polygon",
                        "coordinates": [
                            [ [left, top], [right, top], [right, bottom], [left, bottom], [left, top] ]
                        ]
                     },
                    "properties": {}
                 }
        if colour:
            # >>> "%0.2x" % 1
            # '01'
            # >>> "%0.2x" % 234
            # 'ea'
            feature['properties']['colour'] = '#' + 3 * ("%0.2x" % colour)
        else:
            feature['properties']['gradient_start'], feature['properties']['gradient_stop'] = gradient_stops(left)
        return feature
    
    feature_collection = {
                            'features' : [],
                            'type': 'FeatureCollection'
                          }

    pixels = image.load()
    # This is a slow but straightforward way of going about it:
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            colour = pixels[x,y]
            if colours:
                # We are interested in all pixels that have a shade of grey
                if colour != 255:
                    feature_collection['features'].append(px2feature((x,y), colour))
            else:
                # We are only interested in black pixels
                if colour == 0:
                    feature_collection['features'].append(px2feature((x,y)))
    
    return json.dumps(feature_collection, indent=4)


def find_rainclouds(THIS_GFS_SLUG):
    THIS_GFS_FOLDER = os.path.join(GFS_FOLDER, THIS_GFS_SLUG)
    if not THIS_GFS_FOLDER:
        logger.debug("no grib files found. Run fetch.py?")
        return False
    
    logger.debug("starting cloud analysis with grib information from %s" % THIS_GFS_SLUG)
    
    DATE = datetime.strptime(THIS_GFS_SLUG, "%Y%m%d%H")       # strptime can’t handle timezones, what up with that?
    DATE = DATE.replace(tzinfo=pytz.UTC)                        # we know it’s UTC so we add that info http://stackoverflow.com/questions/7065164/how-to-make-an-unaware-datetime-timezone-aware-in-python

    grib_file_path = os.path.join(THIS_GFS_FOLDER, "GFS_half_degree.%s.pwat.grib" % THIS_GFS_SLUG)
    json_file_path = os.path.join(THIS_GFS_FOLDER, "GFS_half_degree.%s.pwat.json" % THIS_GFS_SLUG)
    png_file_path  = os.path.join(THIS_GFS_FOLDER, "GFS_half_degree.%s.pwat.png" % THIS_GFS_SLUG)
    
    png_clouds_greyscale_file_path    = os.path.join(THIS_GFS_FOLDER, "GFS_half_degree.clouds_greyscale.%s.pwat.png" % THIS_GFS_SLUG)
    png_clouds_greymasked_file_path   = os.path.join(THIS_GFS_FOLDER, "GFS_half_degree.clouds_greymasked.%s.pwat.png" % THIS_GFS_SLUG)
    png_cloud_mask_file_path          = os.path.join(THIS_GFS_FOLDER, "GFS_half_degree.cloud_mask.%s.pwat.png" % THIS_GFS_SLUG)
    png_cloud_mask_extruded_file_path = os.path.join(THIS_GFS_FOLDER, "GFS_half_degree.cloud_mask.extruded.%s.pwat.png" % THIS_GFS_SLUG)
    png_cloud_mask_combined_file_path = os.path.join(THIS_GFS_FOLDER, "GFS_half_degree.cloud_mask.combined.%s.pwat.png" % THIS_GFS_SLUG)
    
    russia_layer = Image.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'russia.png'))
    
    rainbow_json_file_path = os.path.join(THIS_GFS_FOLDER, "%s.rainbows.json" % THIS_GFS_SLUG)
    clouds_json_file_path = os.path.join(THIS_GFS_FOLDER, "%s.clouds.json" % THIS_GFS_SLUG)
    
    if not os.path.exists(grib_file_path):
        logger.debug("expected GRIB file not foud")
        return False
    if os.path.exists(json_file_path):
        logger.debug("corresponding JSON found, skipping JSON conversion")
    else:
        logger.debug("converting GRIB into JSON file: %s" % json_file_path)
        pipe = subprocess.Popen(['grib2json', '-d', '-n',
                             '-o', json_file_path,
                             grib_file_path])
        c = pipe.wait()
        if c != 0:
            logger.error("error in JSON conversion")
            sys.exit()
        
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
    
    def prec2color(prec):
#        return int(255 - prec * 60) 
        return int(255 - prec * 3)
    
    logger.debug("Converting data to color, and writing it to canvas")
    cloud_layer = Image.new("L", (ni, nj))
    cloud_layer.putdata(map(prec2color, data))
    
    cloud_layer_greyscale = cloud_layer
    # Intermediary debug image:
    # cloud_layer_greyscale.save(png_clouds_greyscale_file_path)
    
    
    logger.debug("Pushing the contrast and then tresholding the clouds")
    enhancer = ImageEnhance.Contrast(cloud_layer)
    cloud_layer = enhancer.enhance(8)
    threshold = 191  
    cloud_layer = cloud_layer.point(lambda p: p > threshold and 255)  
    
    cloud_layer_greyscale.paste(cloud_layer, (0,0), cloud_layer)
    
    logger.debug("Calculating the solar altitudes for all combinations of latitude and longitude")
    altitudes = []
    for j in range(nj):
        for i in range(ni):
            altitudes.append(Pysolar.GetAltitudeFast(latitude, longitude, DATE))
            longitude += dl
        latitude += dph
    
    def altitude2colors(altitude):
        if 42 > altitude > 0:
            return 255
        else:
            return 0
    
    sun_mask = Image.new("L", (ni, nj))
    logger.debug("Calculating the colours based on the altitudes")
    colors = map(altitude2colors, altitudes)
    sun_mask.putdata(colors)
    
    # Calculate where the sun is in the image
    sun_i = altitudes.index(max(altitudes))
    sun_y = sun_i / ni
    sun_x = sun_i % ni
    logger.debug("Found the sun at index %s corresponding to %s, %s" % (sun_i, sun_x, sun_y))
    sun_mask.putpixel((sun_x, sun_y), 255)
    
    middle = ni / 2
    translate_x = middle - sun_x
    logger.debug("Moving the image %s pixels to the right to have the sun exactly in the middle" % translate_x)
    cloud_layer = cloud_layer.offset(translate_x)
    
    # Intermediary debug image:
    # cloud_layer.save(png_cloud_mask_file_path.replace(".png", ".not-inverted.png"))
    cloud_layer = ImageOps.invert(cloud_layer)
    cloud_layer.save(png_cloud_mask_file_path)
    
    logger.debug("Barrel distorting the clouds")
    barrel_distortion = "0.0 0.0 0.025 0.975 %s %s" % (sun_x + translate_x, sun_y)
    pipe = subprocess.Popen(['convert', png_cloud_mask_file_path,
                         '-virtual-pixel', 'black',
                         '-filter','point', '-interpolate', 'NearestNeighbor',
                         '-distort', 'Barrel', barrel_distortion,
                         '+antialias',
                         '-negate',
                         png_cloud_mask_extruded_file_path])
    pipe.wait()
    
    logger.debug("Adding the distorted clouds to the original, leaving only rainbow area")
    extruded_cloud_layer = Image.open(png_cloud_mask_extruded_file_path) 
    cloud_layer.paste(extruded_cloud_layer, (0, 0), extruded_cloud_layer)
    
    logger.debug("Moving the image back to its original position")
    cloud_layer = cloud_layer.offset(translate_x * -1)
    
    # Intermediary debug image:
    # cloud_layer.save(png_file_path.replace(".png", ".without-sun-mask.png"))
    logger.debug("Masking where it is night or where the sun is too high to see rainbows")
    cloud_layer.paste(ImageOps.invert(sun_mask), (0, 0), ImageOps.invert(sun_mask))
    
    logger.debug("Showing only rainbows over Russian soil")
    cloud_layer.paste(russia_layer, (0, 0), russia_layer)
    
    logger.debug("Encoding the rainbow locations as geographic features in a JSON file")
    with open(rainbow_json_file_path, 'w') as f:
        f.write(img2features(cloud_layer))
    
    logger.debug("Writing image file")
    cloud_layer.save(png_file_path)
    logger.debug("Written")

    cloud_layer_greyscale.paste(ImageOps.invert(sun_mask), (0, 0), ImageOps.invert(sun_mask))
    cloud_layer_greyscale.paste(russia_layer, (0, 0), russia_layer)
    with open(clouds_json_file_path , 'w') as f:
        f.write(img2features(cloud_layer_greyscale, colours=True))
    cloud_layer_greyscale.save(png_clouds_greymasked_file_path)

if __name__ == '__main__':
    logger.debug('looking for forecasts to process')
    for f in sorted(os.listdir(GFS_FOLDER), reverse=True):
        slug = f
        path = os.path.join(GFS_FOLDER, slug)
        if re.match(r'\d{10}', slug) and os.path.isdir(path):
            if len(glob(os.path.join(path, '*pwat.png'))) > 0:
                logger.debug("encountered already processed forecast %s, stop searching for forecasts" % slug)
                break
            if len(glob(os.path.join(path, '*pwat.grib'))) > 0:
                logger.debug("encountered forecast %s, start processing" % slug)
                find_rainclouds(slug)

