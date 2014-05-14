# -*- coding: utf-8 -*-
# convert elektro_l_20140311_0530_rgb.jpg -brightness-contrast 35x50 elektro_l_20140311_0530_rgb_edt.jpg

import subprocess   
from datetime import datetime

from utils import logger

def fetch_elektro_l(test=False):
    """
    Fetch images from the Russian Satellite Elektro-L
    
    Note: as of 19 apr. 2014 Elektro L is defective.
    By the end of may, reparation efforts will be undertaken.
    
    Let’s hope it works!
    """
    d = datetime.now()
    d = d.replace(minute = 0 if d.minute < 30 else 30)
    
    if test:
        import dateutil.parser
        d = dateutil.parser.parse('2014-01-09T20:30')
    
    url      = d.strftime("ftp://electro:electro@ftp.ntsomz.ru//%Y/%B/%d/%H%M/")  # ftp.ntsomz.ru//2014/April/07/1730/
    filename = d.strftime("%y%m%d_%H%M_RGB.jpg")                                  # 140407_1730_5.jpg
    
    logger.debug("attempting to download Elektro L image %s from %s" % (filename, url))
    
    pipe = subprocess.Popen("""lftp -c 'open -e "mget %s" %s'""" % (filename, url), shell=True, stderr=subprocess.PIPE
                             )
    c = pipe.wait()
    
    if c == 0:
        logger.debug("successfully completed download")
    else:
        logger.error("Elektro L download failed with error: %s" % pipe.stderr.read())

if __name__ == '__main__':
    fetch_elektro_l(test=True)
