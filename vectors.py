#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""  Turns an image into a two-colored grid of vectorpixels: squares,
circles, or squares with rounded corners.

Creating a vector image from a raster image usually consists of
imagining some kind of curve, responsible for the pixels. But this
is guess work at best. Why don’t we work with what’s actually
there—points?

This script turns an image into a grid of vector squares, circles,
or squares with rounded corners.

usage (command line):

python vectorpixel.py inputimage.png > outputimage.svg

 TODO: allow multi-colour pictures, implement vertical and horiontal scanlines """

from PIL import Image
import sys
import os

from settings import LATEST_GFS_FOLDER, LATEST_GFS_SLUG
from utils import logger

class Vectorpixel:
    def __init__(self, image):
        self.i = Image.open(image).convert("1")
        self.px = self.i.load()
        self.constructed = False

    def construct(self, grid=24, line=1, rounded=4, test=(lambda x: x == 0)):
        self.grid = grid
        self.line = line
        self.rounded = rounded
        self.width = self.height = self.grid - 2 * self.line
        self.test = test
        self.fill = '#000000'
        self.constructed = True

    def _yieldlocations(self):
        for x in range(self.i.size[0]):
            for y in range(self.i.size[1]):
                if self.test(self.px[x,y]):
                    yield (x,y)

    def _mkelements(self):
        for l in self._yieldlocations():
            yield "<rect x='%s' y='%s' width='%s' height='%s' rx='%s' fill='%s'/>" % (
    self.grid * l[0] + self.line, self.grid * l[1] + self.line, self.width, self.height, self.rounded, self.fill)

    def _format(self):
        output = '<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="%s">\n' % (self.i.size[0] * self.grid, self.i.size[1] * self.grid)
        for e in self._mkelements():
            output += e
            output += '\n'
        output += '</svg>'
        return output

    def generate(self):
        if not self.constructed:
            self.construct()
        return self._format()

def make_vector_pixels():
    if not LATEST_GFS_FOLDER:
        logger.debug("No GFS files found. Run fetch.py?")
        return False
    
    png_file_path  = os.path.join(LATEST_GFS_FOLDER, "GFS_half_degree.%s.pwat.png" % LATEST_GFS_SLUG)
    svg_file_path = png_file_path.replace(".png", ".svg")
    if not os.path.exists(png_file_path):
        logger.debug("expected PNG file %s not foud" % png_file_path)
        return False
    
    logger.debug("found PNG file %s" % png_file_path)
    logger.debug("generating vector pixels")
    
    v = Vectorpixel(png_file_path)
    v.construct(4, 0, 0)
    with open(svg_file_path, 'w') as f:
        f.write(v.generate())
    
if __name__ == "__main__":
    make_vector_pixels()
    