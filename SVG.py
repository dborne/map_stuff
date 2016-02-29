"""
SVG.py - Construct/display SVG scenes.

The following code is a lightweight wrapper around SVG files. The metaphor
is to construct a scene, add objects to it, and then write it to a file
to display it.
"""

import types


class Scene:
    def __init__(self, name="svg", width=400, height=400):
        self.name = name
        self.items = []
        self.height = height
        self.width = width
        return

    def add(self, item):
        self.items.append(item)

    def __str__(self):
        var = ['<?xml version="1.0" standalone="no"?>',
               '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"',
               '  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">',
               '<svg height="%s" width="%s"' % (self.height, self.width),
               ' xmlns="http://www.w3.org/2000/svg"',
               ' xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1">',
               ]
        for item in self.items:
            var.append(str(item))
        var .append('</svg>\n')
        return '\n'.join(var)

    def write_svg(self, filename=None):
        if filename:
            self.svgname = filename
        else:
            self.svgname = self.name + ".svg"
        file = open(self.svgname, 'w')
        file.write(str(self))
        file.close()
        return

    def clear(self):
        self.items = []


class _svg_element (object):
    def __init__(self, **options):
        self._options = {}
        for key in options.keys():
            if key.startswith('xlink'):
                outkey = key[:5] + ':' + key[5:]
            else:
                outkey = key
            self._options[outkey.replace('_', '-')] = options[key]
        return

    def options(self):
        return ' '.join(['%s="%s"' % x for x in self._options.items()])

    def addopt(self, key, value):
        self._options[key] = value

    def __str__(self):
        return '<%s %s />' % (self.__class__.__name__, self.options())


class _grouped_elem (_svg_element):
    name = "NOT DEFINED"

    def __init__(self, **options):
        self.items = []
        super(_grouped_elem, self).__init__(**options)

    def add(self, item):
        self.items.append(item)

    def __str__(self):
        var = ['<%s %s>' % (self.name, self.options())]
        for item in self.items:
            var.extend(['  %s' % x for x in str(item).split('\n')])
        var.append('</%s>' % self.name)
        return '\n'.join(var)


class group(_grouped_elem):
    name = 'g'
    pass


class defs (_grouped_elem):
    name = 'defs'
    pass


class symbol (_grouped_elem):
    name = 'symbol'
    pass


class line (_svg_element):
    def __init__(self, start, end, **options):
        super(line, self).__init__(x1=start[0],
                                   x2=end[0],
                                   y1=start[1],
                                   y2=end[1],
                                   **options)


class circle (_svg_element):
    def __init__(self, center, radius, **options):
        super(circle, self).__init__(cx=center[0],
                                     cy=center[1],
                                     r=radius,
                                     **options)


class rect (_svg_element):
    pass


class use (_svg_element):
    pass


class polygon (_svg_element):
    def __init__(self, points, **options):
        """polygon(points, {'opt1':'val1', 'opt2':'val2'})
        setup polygon object

        points should be a sequence of x,y tuples or a raw list of
        coordinates options are any SVG options for the polygon (color,
        fill, stroke, etc)
        """
        if type(points[0]) in (types.ListType, types.TupleType):
            pstr = ', '.join([str(x) for y in points for x in y])
        else:
            pstr = ', '.join([str(x) for x in points])
        super(polygon, self).__init__(points=pstr, **options)


class text (_svg_element):
    def __init__(self, txt, **options):
        self.text = txt
        super(text, self).__init__(**options)

    def __str__(self):
        return '<%s %s>%s</%s>' % (self.__class__.__name__,
                                   self.options(),
                                   self.text,
                                   self.__class__.__name__)


def test():
    scene = Scene('test', height='3in', width='5in')
    scene.add(rect(x=".1in", y=".1in",
                   width="4.9in", height="2.9in",
                   rx=".4in", ry=".4in",
                   style="fill:#bbb; stroke:#24c; stroke-width:.01in"))
    scene.add(line((".3in", ".5in"),
                   ("2in", "1.2in"),
                   style="stroke:rgb(99,99,99);stroke-width:2"))
    scene.add(polygon(points=(("220", "100"),
                              ("300", "210"),
                              ("170", "250")),
                      style="fill:#c26;stroke:#000000;stroke-width:1"))
    scene.write_svg()
    return

if __name__ == '__main__':
    test()
