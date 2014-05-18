# -*- coding: utf-8 -*-

"""
We used this shape-file

http://thematicmapping.org/downloads/world_borders.php

Licensed under CC-BY-SA

With GDAL, this set was converted to GEO-JSON, and Russia extracted.

This makes it easy to draw, following this spec:
http://geojson.org/geojson-spec.html
"""


import json

from PIL import Image, ImageDraw

def position_to_point(position):
    return (position[0] * 2, (position[1] - 90) * -2)

with open('russia.json') as f:
    feature = json.loads(f.read())

im = Image.new("L", (720, 361), 255)
draw = ImageDraw.Draw(im)

for polygon in feature['geometry']['coordinates']:
    # the first polygon is an outline: the other polygons are the holes, which we don’t need
    outer_ring = polygon[0]
    # this outer ring is a collection of positions (coordinate pairs)
    # the first and the last position in the outer_ring are the same, so we don’t need the last one:
    # the polygon is closed automatically:
    draw.polygon([position_to_point(position) for position in outer_ring[:-1] ], fill=0)

im.save("russia.png")
