# -*- coding: utf-8 -*-

"""
Some scripts to analyse the rainbow data collected
"""

import os
import json
import re
import sys

from datetime import datetime

from settings import GFS_FOLDER
from glob import glob

if len(sys.argv) != 2:
    sys.exit("""supply argument: `csv` for csv table of number of rainbows over,
or a two digit hour for map of number of rainbows over time at a given hour of day""")

HOST = "http://vps40616.public.cloudvps.com"

if sys.argv[1] == csv:
    format = "csv"
else:
    format = "html"

if format == "html":
    print "<!DOCTYPE html>"
    print '<meta charset="utf-8" />'
    
    print "<table>"
    print "<style>img { opacity: 0.4; } td { position: absolute; left: 0 } td:nth-child(5) { left: 720px} tr { height: 370px }</style>"
    print "<h1>%s:00</h1>" % sys.argv[1]
    
    for f in sorted(os.listdir(GFS_FOLDER), reverse=True):
        slug = f
        path = os.path.join(GFS_FOLDER, slug)
        if re.match(r'\d{8}' + sys.argv[1], slug) and os.path.isdir(path) and int(slug) >= 2014082709:
            
            russia_uri = "%s/static/russia.png" % HOST
            png_file_path  = "%s/static/gfs/%s/GFS_half_degree.%s.pwat.png" % (HOST, slug, slug)
            d = datetime.strptime(slug,'%Y%m%d%H')        
    
            png_sun_mask_file_uri            = "%s/static/gfs/%s/GFS_half_degree.sun_mask.%s.pwat.png" % (HOST, slug, slug)
            png_clouds_greyscale_file_uri    = "%s/static/gfs/%s/GFS_half_degree.clouds_greyscale.%s.pwat.png" % (HOST, slug, slug)
            png_clouds_greymasked_file_uri   = "%s/static/gfs/%s/GFS_half_degree.clouds_greymasked.%s.pwat.png" % (HOST, slug, slug)
            png_clouds_greymasked_before_russia_file_uri   = "%s/static/gfs/%s/GFS_half_degree.clouds_greymasked.before_russia.%s.pwat.png" % (HOST, slug, slug)
            png_cloud_mask_file_uri          = "%s/static/gfs/%s/GFS_half_degree.cloud_mask.%s.pwat.png" % (HOST, slug, slug)
            png_cloud_mask_extruded_file_uri = "%s/static/gfs/%s/GFS_half_degree.cloud_mask.extruded.%s.pwat.png" % (HOST, slug, slug)
            png_cloud_mask_combined_file_uri = "%s/static/gfs/%s/GFS_half_degree.cloud_mask.combined.%s.pwat.png" % (HOST, slug, slug)
            print '<tr><td><img src="%s" /></td><td><img src="%s" /></td><td><img src="%s" /></td><td><img src="%s" /></td><td>%s</td></tr>' % (png_cloud_mask_file_uri.replace(".png", ".not-inverted.png"), png_sun_mask_file_uri, png_file_path, russia_uri, d.isoformat())
    print "</table>"

if format == "csv":
    for f in sorted(os.listdir(GFS_FOLDER), reverse=True):
        slug = f
        path = os.path.join(GFS_FOLDER, slug)
        if re.match(r'\d{10}', slug) and os.path.isdir(path):
            rainbow_cities = glob(os.path.join(path, '*rainbow_cities.json'))
            if len(rainbow_cities) != 1:
                continue
            rainbow_city = os.path.join(path, slug, rainbow_cities[0])
            with open(rainbow_city) as f:
                rainbows = json.load(f)
            d = datetime.strptime(slug,'%Y%m%d%H')
            print "%s,%s" % (d.isoformat(), len(rainbows))
