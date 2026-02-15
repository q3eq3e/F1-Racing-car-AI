from typing import Tuple, List
from shapely import Polygon, LineString, Point
from shapely.ops import nearest_points
import numpy as np


def rotate(xy, angle):
    rot_mat = np.array(
        [[np.cos(angle), np.sin(angle)], [-np.sin(angle), np.cos(angle)]]
    )
    return np.matmul(xy, rot_mat)


def get_finish_line(layout, finish_point) -> LineString:
    """Finds closest points on the inside and outside edges of the track layout to specific point and creates a line"""
    finish_point = Point(*finish_point)
    outside_point, _ = nearest_points(layout.exterior, finish_point)
    inside_point, _ = nearest_points(layout.interiors[0], finish_point)
    return LineString([outside_point, inside_point])


# def _vector_angle(start_point, end_point):
#     return np.atan2(end_point[1] - start_point[1], end_point[0] - start_point[0])


# def change_side_of_line(start_point, end_point, line_start, line_end):
#     def between(a, b, c):
#         return a < b and b < c

#     finish_line_angle = np.degrees(_vector_angle(line_start, line_end))
#     finish_line_angle2 = (np.degrees(_vector_angle(line_start, line_end)) + 180) % 360
#     start_angle = np.degrees(_vector_angle(line_start, start_point))
#     end_angle = np.degrees(_vector_angle(line_start, end_point))

#     if start_angle == end_angle:
#         return False
#     if start_angle == finish_line_angle or start_angle == finish_line_angle2:
#         return False
#     if end_angle == finish_line_angle or end_angle == finish_line_angle2:
#         return True

#     return between(start_angle, finish_line_angle, end_angle) ^ between(
#         start_angle, finish_line_angle2, end_angle
#     )
