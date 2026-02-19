from shapely import Point


class Move:
    def __init__(self, prev_point, next_point):
        self.prev = Point(prev_point)
        self.next = Point(next_point)
