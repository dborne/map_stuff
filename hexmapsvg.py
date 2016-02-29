import math
import types
from functools import reduce
from operator import add

import SVG


def get_translator(value):
    def _translate(c):
        return((c[0]+_translate.value[0], c[1]+_translate.value[1]))
    _translate.value = value
    return _translate


class Hexmap:
    def __init__(self, side=10, spacing=0, style="fill: #fff; stroke: #000; stroke-width: 1"):
        # |-h|-s--|
        # |  |____|  ______
        # |  /    \       r
        # | /      \ ______
        #   \      /
        #    \____/
        #
        self.space = spacing
        self._resize(side)
        self.style = style
        return

    def _resize(self, side):
        self.s = s = side
        self.h = h = s / 2  # side*sin(30); cos(30)=.5
        self.r = r = int(s * math.sqrt(3) / 2)  # side*cos(30); cos(30)=sqrt(3)/2
        self.hex0 = ((0, r), (h, 0), (h+s, 0), (2*h+s, r), (h+s, 2*r), (h, 2*r))
        self.xoffset = (h + s + self.space)
        self.yoffset = (2 * r + self.space)
        self.yodd = r + (self.space / 2)

    def drawhex(self, scene, coords, localstyle=None):
        "draw the hex given the hex grid coordinates"
        (x, y) = coords
        translate = get_translator((x * self.xoffset, y * self.yoffset + (x % 2) * self.yodd))
        hex = [translate(indices) for indices in self.hex0]
        if localstyle is None:
            localstyle = self.style
        scene.add(SVG.polygon(hex, style=localstyle))

    def fullgrid(self, width, height):
        "draw a full hex grid to the extent of the width and height given"
        sc_width = (self.h + self.s + self.space) * width + self.h - self.space
        sc_height = (2 * self.r + self.space) * height + self.r
        scene = SVG.Scene('hexgrid', sc_width, sc_height)
        for x in range(width):
            for y in range(height):
                self.drawhex(scene, (x, y))
        return scene

    def hexellate(self, img, threshold=None):
        """
        Convert an image (assuming an rgb PIL image) file into a hexmap.
        If given a threshold, draw a hex only when above this threshold,
        otherwise draw a hex filled with the color in the hex's center pixel
        """
        sc_width, sc_height = img.size
        scene = SVG.Scene('hexmap', sc_width, sc_height)
        width = sc_width/(self.h + self.s + self.space)
        height = sc_height/(2 * self.r + self.space)
        if threshold:
            if type(threshold) in (types.ListType, types.TupleType):
                comp = lambda px: (
                    px[0] > threshold[0] and px[1] > threshold[1] and px[2] > threshold[2])
            else:
                comp = lambda px: (sum(px) > 3*threshold)

            def style(pixel):
                if comp(pixel):
                    return "fill: #fff; stroke: #000; stroke-width: 1"
                else:
                    return "fill: none; stroke: none;"
        else:

            def style(pixel):
                return "fill: #%02x%02x%02x; stroke: #000; stroke-width: 1" % pixel

        for x in range(width):
            for y in range(height):
                center = img.getpixel((x * self.xoffset + self.s,
                                       y * self.yoffset + (x % 2) * self.yodd + self.r))
                self.drawhex(scene, (x, y), style(center))
        return scene

    def map2grid(self, map, win_size=2, threshold=.5):
        size_x = len(map[0])
        size_y = len(map)
        threshval = win_size**2 * threshold
        ret = []
        for yindex in range(0, size_y, win_size):
            row = []
            for xindex in range(0, size_x, win_size):
                if xindex % 2:
                    yindex += win_size/2

                # TODO: clean this up
                res = reduce(
                    add,
                    reduce(
                        add,
                        [val[xindex:xindex+win_size] for val in map[yindex:yindex + win_size]])
                )
                row.append(int(res > threshval))
            ret.append(row)
        return ret

    def clear(self):
        self.scene.clear()

    def write(self):
        self.scene.write_svg()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Build an svg hexmap')
    parser.add_argument('width', type=int, help="width of the map in hexes")
    parser.add_argument('height', type=int, help="height of the map in hexes")
    parser.add_argument('hex_size', type=int, help="length, in pixels, of the side of the hex")
    parser.add_argument('-s', '--spacing', type=int, default="0",
                        help="space, in pixels, between the hexes (default=0)")
    parser.add_argument('-f', '--filename', default="grid", help="name of .svg file")

    args = parser.parse_args()
    hm = Hexmap()
    scene = hm.fullgrid(args.width, args.height, args.hex_size, args.spacing)
    scene.name = args.filename
    scene.write_svg()
