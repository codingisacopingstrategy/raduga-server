# -*- coding: utf-8 -*-

import math

from settings import *

def deg2px(lat_deg, lon_deg, zoom=4):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom * 256
    xpx = int((lon_deg + 180.0) / 360.0 * n)
    ypx = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xpx, ypx)

def num2deg(xtile, ytile, zoom=4):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)

def px2deg(x, y, zoom=4):
    global TILE_SIZE
    xtile = x / float(TILE_SIZE) + 0.5 / TILE_SIZE
    ytile = y / float(TILE_SIZE) + 0.5 / TILE_SIZE
    return num2deg(xtile, ytile, zoom)
