#!/bin/bash
SLUG=$1
cd /home/e/apps/raduga-server/static/gfs/$SLUG

mv $SLUG.clouds.json $SLUG.clouds.json.bak
convert GFS_half_degree.clouds_greymasked.$SLUG.pwat.png -negate -threshold 0 -negate GFS_half_degree.clouds_blackmasked.$SLUG.pwat.ppm
potrace --turnpolicy black --turdsize 0 --alphamax 0 --backend geojson --scale 0.5 --leftmargin -0.25 --bottommargin -90.25 --output $SLUG.clouds.json GFS_half_degree.clouds_blackmasked.$SLUG.pwat.ppm

mv $SLUG.rainbows.json $SLUG.rainbows.json.bak
convert GFS_half_degree.$SLUG.pwat.png GFS_half_degree.$SLUG.pwat.ppm
potrace --turnpolicy black --turdsize 0 --alphamax 0 --backend geojson --scale 0.5 --leftmargin -0.25 --bottommargin -90.25 --output $SLUG.rainbows.json GFS_half_degree.$SLUG.pwat.ppm
