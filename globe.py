# -*- coding: utf-8 -*-
# convert elektro_l_20140311_0530_rgb.jpg -brightness-contrast 35x50 elektro_l_20140311_0530_rgb_edt.jpg

import os
import sys
import subprocess
from datetime import datetime

import dateutil.parser

from utils import logger
from settings import ELEKTRO_L_FOLDER, ELEKTRO_L_SRC_FOLDER

def pretty_globe(filename):
    image_path           = os.path.join(ELEKTRO_L_SRC_FOLDER, filename)
    mask_path            = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'elektro_l_mask.png')
    image_processed_path = os.path.join(ELEKTRO_L_FOLDER, filename).replace('.jpg', '.png')

    
    # The Elektro L engineers used smaller file sizes in the beginning of 2013:
    if int(os.path.basename(filename)[:2]) < 14 and int(os.path.basename(filename)[2:4]) < 4:
        mask_path            = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'elektro_l_mask_800.png')
    
    pipe = subprocess.Popen(['convert', image_path,
                     '-brightness-contrast', '35x50',
                     mask_path, '-alpha', 'Off', '-compose', 'CopyOpacity', '-composite',
                     image_processed_path])
    pipe.wait()

def fetch_elektro_l(d):
    """
    Fetch images from the Russian Satellite Elektro-L
    The argument d is a python datetime object
    
    Note: as of 19 apr. 2014 Elektro L is defective.
    By the end of may, reparation efforts will be undertaken.
    
    Let’s hope it works!
    """
    
    ELEKTRO_L_SRC_FOLDER = os.path.join(ELEKTRO_L_FOLDER, 'src')
    
    # Elektro L images are every half hour
    d = d.replace(minute = 0 if d.minute < 30 else 30)
    
    url      = d.strftime("ftp://electro:electro@ftp.ntsomz.ru//%Y/%B/%d/%H%M/")  # ftp.ntsomz.ru//2014/April/07/1730/
    filename = d.strftime("%y%m%d_%H%M_RGB.jpg")                                  # 140407_1730_5.jpg
    
    logger.debug("attempting to download Elektro L image %s from %s" % (filename, url))
    
    pipe = subprocess.Popen("""lftp -c 'open -e "mget -O %s %s" %s'""" % (ELEKTRO_L_SRC_FOLDER, filename, url), shell=True, stderr=subprocess.PIPE
                             )
    c = pipe.wait()
    
    if c == 0:
        logger.debug("successfully completed download")
        logger.debug("visual processing of image")
        pretty_globe(filename)
        logger.debug("image written")
    else:
        logger.error("Elektro L download failed with error: %s" % pipe.stderr.read())

if __name__ == '__main__':
    """
    Usage: python globe.py "2014-05-26T09:36:43.010Z"
    """
    if len(sys.argv) == 1:
        d = datetime.now()
        fetch_elektro_l(d)
    else:
        for dstring in sys.argv[1:]:
            d = dateutil.parser.parse(dstring)
            fetch_elektro_l(d)
    
    """
    # Example of using the fetch_elektro function from the globe module
    # from within a python script:
    
    from datetime import timedelta, datetime

    import pytz
    from globe import fetch_elektro_l
    
    half_hour = timedelta(minutes=30)
    # In 2013, images start the 6th of February
    date = datetime(2013, 2, 6, 0, 0, 0, 0, pytz.UTC)
    
    
    # There are 17520 half hours in 2013
    
    while date.year == 2013:
        # In 2013, there happen to be no images in april 
        if date.month == 4:
            date = date.replace(month=5)
        fetch_elektro_l(date)
        date = date + half_hour
    """
    
    """
    # Example of using the pretty_globe function from a within a python script
    
    import os
    from glob import glob
    
    from settings import ELEKTRO_L_FOLDER, ELEKTRO_L_SRC_FOLDER
    from globe import pretty_globe
            
    for image_filename in glob(os.path.join(ELEKTRO_L_SRC_FOLDER, "*_RGB.jpg")):
        pretty_globe(image_filename)
    """