from typing import Tuple, List
from shapely import Polygon, LineString, Point
from shapely.ops import nearest_points
import math
import numpy as np


def rotate(xy, angle):
    rot_mat = np.array(
        [[np.cos(angle), np.sin(angle)], [-np.sin(angle), np.cos(angle)]]
    )
    return np.matmul(xy, rot_mat)


def get_finish_line(layout, finish_point):
    """Finds closest points on the inside and outside edges of the track layout to specific point and creates a line"""
    finish_point = Point(*finish_point)
    outside_point, _ = nearest_points(layout.exterior, finish_point)
    inside_point, _ = nearest_points(layout.interiors[0], finish_point)
    return LineString([outside_point, inside_point])
    # return LineString([outer[0], inner[0]])


def get_borders(x_coords: List[float], y_coords: List[float], width) -> Tuple:
    line = list(zip(x_coords, y_coords))
    left_borders = []
    right_borders = []
    for idx, point in enumerate(line):
        if idx > 0:
            prev_point = line[idx - 1]
        else:
            prev_point = line[-1]
        if idx < len(line) - 1:
            next_point = line[idx + 1]
        else:
            next_point = line[0]

        left_edge, right_edge = get_edges(prev_point, point, next_point, width)
        left_borders.append(left_edge)
        right_borders.append(right_edge)

    left_borders = tuple(left_borders)
    right_borders = tuple(right_borders)
    left_polygon = Polygon(left_borders)
    right_polygon = Polygon(right_borders)

    if right_polygon.area <= 0 or left_polygon.area <= 0:
        raise ValueError("Unable to create track")

    inner_border, outer_border = (
        (left_borders, right_borders)
        if right_polygon.area > left_polygon.area
        else (right_borders, left_borders)
    )
    return outer_border, inner_border
    # return Polygon(shell=outer_border, holes=[inner_border])


def get_edges(
    prev_point: Tuple[float, float],
    curr_point: Tuple[float, float],
    next_point: Tuple[float, float],
    width,
) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    diff_x = next_point[0] - prev_point[0]
    diff_y = next_point[1] - prev_point[1]
    vector_len = math.sqrt(diff_x**2 + diff_y**2)
    if vector_len == 0:
        raise ValueError("Next and previous points have to be different")
    normalised_x = diff_x / vector_len
    normalised_y = diff_y / vector_len
    left_point = (
        curr_point[0] - normalised_y * width,
        curr_point[1] + normalised_x * width,
    )
    right_point = (
        curr_point[0] + normalised_y * width,
        curr_point[1] - normalised_x * width,
    )
    return left_point, right_point


def _vector_angle(start_point, end_point):
    return np.atan2(end_point[1] - start_point[1], end_point[0] - start_point[0])


def change_side_of_line(start_point, end_point, line_start, line_end):
    def between(a, b, c):
        return a < b and b < c

    finish_line_angle = np.degrees(_vector_angle(line_start, line_end))
    finish_line_angle2 = (np.degrees(_vector_angle(line_start, line_end)) + 180) % 360
    start_angle = np.degrees(_vector_angle(line_start, start_point))
    end_angle = np.degrees(_vector_angle(line_start, end_point))

    if start_angle == end_angle:
        return False
    if start_angle == finish_line_angle or start_angle == finish_line_angle2:
        return False
    if end_angle == finish_line_angle or end_angle == finish_line_angle2:
        return True

    return between(start_angle, finish_line_angle, end_angle) ^ between(
        start_angle, finish_line_angle2, end_angle
    )
