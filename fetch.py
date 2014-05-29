# -*- coding: utf-8 -*-

import urllib
from datetime import datetime, timedelta
import os

from settings import TILE_SERVER, TILE_FOLDER, GFS_FOLDER
from utils import logger

class AppURLopener(urllib.FancyURLopener):
    version = 'Mozilla/5.0'
 
urllib._urlopener = AppURLopener()


def fetch_owm():
    """
    Download the latest precipitation tiles from Open Weather Map.
    At zoom level 4, there are 4² × 4² = 16 × 16 = 256 tiles.
    """
    ZOOM_LEVEL = z =  4
    
    def quantisised_time():
        """
        ISO representation of datetime rounded to nearest hour.
        To use for folder names etcetera.
        """
        return datetime.now().strftime("%Y-%m-%dT%H:00:00Z")
    
    
    for x in range(z ** 2):
        for y in range(z ** 2):
            uri = TILE_SERVER.format(s='a', z=z, x=x, y=y)
            # make a folder like raduga_tiles/4/5/
            path = os.path.join(TILE_FOLDER, quantisised_time(), str(z), str(x))
            if not os.path.exists(path):
                os.makedirs(path)
            output_file = os.path.join(path, '%s.png' % y)
            urllib.urlretrieve(uri, output_file)

def fetch_gfs():
    """
    Download the latest forecast from the Global Forecast System,
    Already filtered for Precipitable Water.
    """
    six_hours  = timedelta(hours=6)
    nine_hours = timedelta(hours=9)
    d = datetime.utcnow()
    
    # Possible values for hour: [0, 6, 12, 18]
    # We do integer division by 6 to round to 6.
    d_rounded = d.replace(hour = d.hour / 6 * 6)
    
    while True:
        """
        Possible values for hour: [0, 6, 12, 18]
        
        If we don’t find the latest forecast we’ll try to go six hours each time until we get
        one that does exist (or one that we have already downloaded).
        """
        res, res6, res9 = None, None, None
        
        logger.debug("rounding %s hours UTC at %s to %s hours UTC at %s" % 
                     (d.strftime("%H"), d.strftime("%d"), d_rounded.strftime("%H"), d_rounded.strftime("%m")))

        d6 = d_rounded + six_hours
        d9 = d_rounded + nine_hours
        
        slug  = d_rounded.strftime("%Y%m%d%H") # '2014040812'
        slug6 = d6.strftime("%Y%m%d%H") # '2014040812'
        slug9 = d9.strftime("%Y%m%d%H") # '2014040812'
        
        target_folder6 = os.path.join(GFS_FOLDER, slug6)
        target_folder9 = os.path.join(GFS_FOLDER, slug9)
        
        output_file6 = os.path.join(target_folder6, "GFS_half_degree.%s.pwat.grib" % slug6)
        output_file9 = os.path.join(target_folder9, "GFS_half_degree.%s.pwat.grib" % slug9)
        
        if os.path.exists(output_file9):
            # There is no need to continue looking, as we have this file already,
            # and apparently it is the most recent forecast.
            logger.debug("file %s exists already" % output_file)
            break
        
        # uri = "http://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_hd.pl?file=gfs.t" + d_rounded.strftime("%H") + "z.mastergrb2f00&lev_entire_atmosphere_%5C%28considered_as_a_single_layer%5C%29=on&var_PWAT=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgfs." + slug + "%2Fmaster"
        # We get forecasts for 6 and 9 hours later:
        uri6 = "http://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_hd.pl?file=gfs.t" + d_rounded.strftime("%H") + "z.mastergrb2f06&lev_entire_atmosphere_%5C%28considered_as_a_single_layer%5C%29=on&var_PWAT=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgfs." + slug + "%2Fmaster"
        uri9 = "http://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_hd.pl?file=gfs.t" + d_rounded.strftime("%H") + "z.mastergrb2f09&lev_entire_atmosphere_%5C%28considered_as_a_single_layer%5C%29=on&var_PWAT=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgfs." + slug + "%2Fmaster"
        
        logger.debug("retrieving file %s" % uri9)
        res9 = urllib.urlopen(uri9)
        c = res9.getcode()
        if c == 200:
            logger.debug("retrieving file %s" % uri6)
            res6 = urllib.urlopen(uri6) 
            break
        
        if c == 404:
            logger.debug("uri %s not available (yet)" % uri9)
        else:
            logger.debug("uri %s failed with error code %s" % (uri9, c))
        
        d_rounded = d_rounded - six_hours
    
    if res9 and res6:
        for target_folder in [target_folder9, target_folder6]:
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)
        with open(output_file6, 'wb') as f:
            logger.debug("writing file %s" % output_file6)
            f.write(res6.read())
        with open(output_file9, 'wb') as f:
            logger.debug("writing file %s" % output_file9)
            f.write(res9.read())

if __name__ == '__main__':
    fetch_gfs()
