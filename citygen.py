import SVG
import random
import math
from bisect import bisect_left, bisect_right

import networkx as nx

# Highways:
# random start point (later: determine starting point based on geographical concerns)
# random direction (constrained?)
# random distance (constrained)
# collision check
# end check


"""
Experimenting with city map generation:

all roads are lists of segments. segments have bounding boxes that can be quickly checked for
possible collisions.  if bounding boxes collide, then check for detailed collision

so extending a road is generating a random segment, check for collisions and resolve collisions -
either cross (breaking segments in pieces?), end on the collision or shift to a nearby node on the
colliding segment

need some way to look up bounding boxes quickly...sweep and prune?

"""

city = SVG.Scene('citymap', 1000, 1000)


class roadseg (object):
    _delta = 1e-2

    def __init__(self, start, end):
        self.edge = (start, end)
        self.xmin = min(start[0], end[0])
        self.xmax = max(start[0], end[0])
        self.ymin = min(start[1], end[1])
        self.ymax = max(start[1], end[1])

    def __getitem__(self, key):
        return self.edge[key]

    def __eq__(self, other):
        if hasattr(other, 'edge'):
            return ((self._check(self.edge[0], other.edge[0])
                     and self._check(self.edge[1], other.edge[1]))
                    or (self._check(self.edge[0], other.edge[1])
                        and self._check(self.edge[1], other.edge[0])))
        else:
            try:
                return ((self._check(self.edge[0], other[0])
                         and self._check(self.edge[1], other[1]))
                        or (self._check(self.edge[0], other[1])
                            and self._check(self.edge[1], other[0])))
            except:
                return False

    def __ne__(self, other):
        return not(self.__eq__(other))

    def __repr__(self):
        return "{0}({1}, {2})".format(self.__class__.__name__,
                                      repr(self.edge[0]),
                                      repr(self.edge[1]))

    def _check(self, one, two):
        """ Check that segments are within delta of each other"""
        return ((one[0]-two[0] < self._dealta) and (one[1]-two[1] < self._delta))

    def render(self, roadcolor="#333"):
        return SVG.line(*self.edge, style="fill: none; stroke: "+roadcolor+"; stroke-width: 2")


def sweep(seg, listofsegs):
    "Sweep and prune by bounding boxes of segments"
    items = sorted(listofsegs, key=lambda r: r.xmax)
    keys = [item.xmax for item in items]
    start = bisect_left(keys, seg.xmin)

    items = sorted(items[start:], key=lambda r: r.xmin)
    keys = [item.xmin for item in items]
    end = bisect_right(keys, seg.xmax)

    items = sorted(items[:end], key=lambda r: r.ymax)
    keys = [item.ymax for item in items]
    start = bisect_left(keys, seg.ymin)

    items = sorted(items[start:], key=lambda r: r.ymin)
    keys = [item.ymin for item in items]
    end = bisect_right(keys, seg.ymax)
    return items[:end]


def test1():
    city.clear()
    randcoord = lambda: (random.randrange(500), random.randrange(500))
    test = [roadseg(randcoord(), randcoord()) for x in range(20)]
    [seg.render(city) for seg in test]

    x = roadseg(randcoord(), randcoord())
    x.render(city, "#3e3", "#7f7")

    collisions = sweep(x, test)
    [seg.render(city, "#e33", "#f77") for seg in collisions]

    city.write_svg()


def cross(one, two):
    "2d vector cross product"
    return (one[0]*two[1] - one[1]*two[0])


def intersect(one, two, join=False):
    "Check two edges for an intersection. Return the point of intersection, if any."
    # https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
    p = one[0]
    r = (one[1][0]-one[0][0], one[1][1]-one[0][1])
    q = two[0]
    s = (two[1][0]-two[0][0], two[1][1]-two[0][1])

    u1 = cross((q[0]-p[0], q[1]-p[1]), r)
    t1 = cross((q[0]-p[0], q[1]-p[1]), s)
    den = cross(r, s)
    ret = None
    # note: for (r x s) = 0 segments are either parallel or collinear
    if (abs(den) > 1e-4) and (0 < u1/den < 1) and (0 < t1/den < 1):
        u = u1/den
        ret = (q[0] + s[0]*u, q[1] + s[1]*u)
        if join:
            s1 = one[0]
            e1 = one[1]
            s2 = two[0]
            e2 = two[1]
            roads.remove_edges_from((one.edge, two.edge))
            newsegs = ((s1, ret), (ret, e1), (s2, ret), (ret, e2))
            for newseg in newsegs:
                roads.add_edge(*newseg, roadseg=roadseg(*newseg))
            roadsegs = [x[2]['roadseg'] for x in roads.edges(data=True)]
            # roadsegs.extend([roadseg(*x) for x in newsegs])
            # WORKING HERE
    return (ret)


def edge2vec(edge):
    "convert to polar coords"
    mag = math.hypot(edge[1][0]-edge[0][0], edge[1][1]-edge[0][1])
    thet = math.atan2((edge[1][1]-edge[0][1]), (edge[1][0]-edge[0][0]))
    return (mag, thet)


def vec2edge(start, vec):
    "convert to rectangular coords"
    return (start[0]+vec[0]*math.cos(vec[1]), start[1]+vec[0]*math.sin(vec[1]))


def neighborhood(point, range=10):
    "find nearby nodes in the point's neighborhood"

    items = sorted(roads.nodes(), key=lambda r: r[0])
    keys = [item[0] for item in items]
    start = bisect_left(keys, point[0]-range)
    end = bisect_right(keys, point[0]+range)

    items = sorted(items[start:end], key=lambda r: r[1])
    keys = [item[1] for item in items]
    start = bisect_left(keys, point[1]-range)
    end = bisect_right(keys, point[1]+range)

    # sort by distance from point
    return sorted([(item, edge2vec((point, item)))
                   for item in items[start:end]], key=lambda r: r[1][0])


def population_seed():
    for x in range(random.randrange(1, 5)):
        popmap.append((random.randrange(200, 800), random.randrange(200, 800)))


def popweight(point):
    "Do something that gives a bigger value nearer to the population centers"
    maxdist = math.hypot(1000, 1000)
    dists = [x[0] for x in [edge2vec((point, y)) for y in popmap]]
    wdists = [maxdist-x for x in dists]
    return sum(wdists)


def hwysearch(start, length, angle, search_angle=1.5):
    trycount = 4
    curweight = 0
    selected_angle = 0
    while trycount:
        angdelt = random.random()*search_angle - search_angle/2.0
        weight = popweight(vec2edge(start, (length, angle)))
        if weight > curweight:
            curweight = weight
            selected_angle = angle+angdelt
            trycount = 4
        else:
            trycount -= 1
    return selected_angle


def highwaygen():
    start = (random.randrange(250, 750), random.randrange(250, 750))
    n = neighborhood(start)
    if n:
        start = n[0][0]  # closest point
    # angle = random.random() * 6.283 - 3.142
    length = random.randrange(10, 50)
    angle = hwysearch(start, length, 0, 6.283)
    end = vec2edge(start, (length, angle))
    road = addseg(start, end)
    (length, angle) = edge2vec(road.edge)

    for x in range(20):
        length = random.randrange(10, 50)
        start = road[1]
        # angle = angle + random.triangular(-.5,.5)
        angle = hwysearch(start, length, angle)
        end = vec2edge(start, (length, angle))
        road = addseg(start, end)
        (length, angle) = edge2vec(road.edge)


def addseg(start, end):
    n = [item for item in neighborhood(end) if item[0] != start]

    if n:
        end = n[0][0]  # simple version: closest point
        print("end adjusted to nearby point: %s" % (repr(end)))

    road = roadseg(start, end)
    roads.add_edge(*road.edge, roadseg=road)
    roadsegs.append(road)
    collisions = sweep(road, roadsegs)
    for seg in collisions:
        x = intersect(road, seg, join=True)
        if x:
            # print ('%s crosses %s at %s' %(newroad, seg, x))
            city.add(SVG.circle(center=x, radius=4, stroke="#f33", fill="none"))
    return road


def drawfromnetwork(scene):
    for edge in roads.edges():
        scene.add(SVG.line(*edge, style="fill: none; stroke: #333; stroke-width: 2"))
    for x in popmap:
        scene.add(SVG.circle(x, 2, fill='none', stroke='#88e', stroke_width='2'))

roads = nx.Graph()
roadsegs = []
popmap = []
