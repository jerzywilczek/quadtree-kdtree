from enum import IntEnum
from typing import List
import random
import copy
from draw_tool import *

from geometry import Point, Rectangle


class Quadrant(IntEnum):
    NE = 0
    NW = 1
    SW = 2
    SE = 3


class _Node:

    def __init__(self, n, s, w, e, quadrant, parent):
        self.pos = None
        self.max_y = n
        self.min_y = s
        self.min_x = w
        self.max_x = e
        self.mid_y = (self.min_y + self.max_y) / 2
        self.mid_x = (self.min_x + self.max_x) / 2
        self.quadrant = quadrant
        self.parent = parent
        self.children = None

    def in_boundary(self, point: Point) -> bool:  # todo zmienić słabe nierówności + nie jest używane
        return self.min_y <= point[1] <= self.max_y and self.min_x <= point[0] <= self.max_x

    def add_child(self, node):
        if self.children is None:
            self.children = [None for _ in range(4)]
        self.children[node.quadrant] = node


class Quadtree:

    def __init__(self, points: List[Point]):
        n = max(points, key=lambda p: p[1])[1]
        s = min(points, key=lambda p: p[1])[1]
        w = min(points, key=lambda p: p[0])[0]
        e = max(points, key=lambda p: p[0])[0]
        self.root = _Node(n, s, w, e, None, None)
        points = copy.deepcopy(points)
        random.shuffle(points)
        self.__create_quadtree(self.root, points)

    def __create_quadtree(self, node: _Node, points: List[Point]):
        if len(points) == 1:
            node.pos = points[0]
        if len(points) <= 1:
            return
        ne = _Node(node.max_y, node.mid_y, node.mid_x, node.max_x, Quadrant.NE, node)
        nw = _Node(node.max_y, node.mid_y, node.min_x, node.mid_x, Quadrant.NW, node)
        sw = _Node(node.mid_y, node.min_y, node.min_x, node.mid_x, Quadrant.SW, node)
        se = _Node(node.mid_y, node.min_y, node.mid_x, node.max_x, Quadrant.SE, node)

        points_ne = [p for p in points if p[0] > node.mid_x and p[1] >= node.mid_y]
        points_nw = [p for p in points if p[0] <= node.mid_x and p[1] > node.mid_y]
        points_sw = [p for p in points if p[0] < node.mid_x and p[1] <= node.mid_y]
        points_se = [p for p in points if p[0] >= node.mid_x and p[1] < node.mid_y]

        node.add_child(ne)
        self.__create_quadtree(ne, points_ne)
        node.add_child(nw)
        self.__create_quadtree(nw, points_nw)
        node.add_child(sw)
        self.__create_quadtree(sw, points_sw)
        node.add_child(se)
        self.__create_quadtree(se, points_se)

    def __find(self, node: _Node, rect: Rectangle, res: List[Point]):
        if rect.min_x > node.max_x or rect.max_x < node.min_x or rect.min_y > node.max_y or rect.max_y < node.max_y:
            return
        if node.children is None:
            if node.pos is not None and rect.point_inside(node.pos):
                res.append(node.pos)
            return
        for ch in node.children:
            self.__find(ch, rect, res)

    def find(self, rect: Rectangle) -> List[Point]:
        res = []
        self.__find(self.root, rect, res)
        return res


class View:

    def __init__(self, points: List[Point], rect: Rectangle, quadtree: Quadtree):
        self.scenes = []
        self.quadrants = []
        self.points = PointsCollection(points)
        self.rect = LinesCollection(
            [[(rect.min_x, rect.min_y), (rect.max_x, rect.min_y)], [(rect.max_x, rect.min_y), (rect.max_x, rect.max_y)],
             [(rect.max_x, rect.max_y), (rect.min_x, rect.max_y)]],
            color='brown')

    def __gen_quadrants(self, node: _Node):
        self.quadrants.extend(
            [[(node.min_x, node.min_y), (node.max_x, node.min_y)], [(node.max_x, node.min_y), (node.max_x, node.max_y)],
             [(node.max_x, node.max_y), (node.min_x, node.max_y)]])
        if node.children is not None:
            for ch in node.children:
                if ch is not None:
                    self.__gen_quadrants(node)


points0 = [tuple([0.0, 1.0]), tuple([5.0, 2.0]), tuple([2.0, 2.0]), tuple([5.0, 3.0]), tuple([0.0, 0.0]),
           tuple([2.0, 3.0]), tuple([6.0, 2.0]), tuple([3.0, 2.0])]
Qt = Quadtree(points0)
rect0 = Rectangle(1, 4, 1, 3)

print(Qt.find(rect0))
