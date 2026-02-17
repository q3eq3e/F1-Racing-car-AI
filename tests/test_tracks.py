from F1_track.tracks import Track, get_all_tracks_by_year
from shapely import Point
import pytest


def test_config():
    assert True == True


def test_create_track():
    track = Track("Austrian")
    assert track is not None
    assert not track.layout.is_empty
    assert track.layout.is_valid
    assert len(track.layout.interiors) == 1
    assert track.length > 1e4 and track.length < 1e6
    assert track.name == "Austrian"
    assert track.width == 400
    assert track.layout.contains(track.finish_line)
    assert all(
        [
            track.layout.boundary.dwithin(Point(point), 1e-6)
            for point in list(zip(*track.finish_line.xy))
        ]
    )
    assert track.finish_line.length - track.width < 1e-3
    assert track.layout.contains(track.starting_point)
    assert track.finish_line.dwithin(track.starting_point, 1e-6)
    assert track.finish_line.centroid == track.starting_point


def test_change_width():
    track = Track("Austrian", width=100)
    assert track.layout.is_valid
    assert len(track.layout.interiors) == 1
    assert track.width == 100


def test_different_years():
    track1 = Track("Abu Dhabi", year=2024)
    track2 = Track("Abu Dhabi", year=2019)
    assert track1.length != track2.length
    assert abs(track1.length - track2.length) > 10


def test_too_wide():
    with pytest.raises(ValueError):
        Track("British", width=1000)


def test_japan():
    with pytest.raises(ValueError):
        Track("Japanese")


def test_saving_and_loading_track():
    track = Track("Italian")
    assert track.length > 0
    track.save("../../../tests/temp/test.pkl")
    del track
    with pytest.raises(Exception):
        track
    track = Track.load("../../../tests/temp/test")
    assert track.length > 0


def test_all_tracks():
    tracks = get_all_tracks_by_year(2024)
    assert len(tracks) == 23
    for track in tracks:
        assert track.layout.is_valid
        assert track.length > 0


def test_valid_move_positive():
    track = Track("Austrian")
    start = track.starting_point
    moves = [
        ((-2000, -2000), True),
        ((-2000, -2000), True),
        ((-1900, -2000), True),
        (Point(-1900, -1990), True),
        ((-2000, -1000), False),
        ((-2000, -1000), False),
        ((-3000, -1000), False),
        (Point(-3000, -1000), False),
        ((-5000, -1000), False),
        ((-4000, -1000), False),
        ((-2000, -2000), False),
        ((-2500, -2300), True),
        ((-3300, -2000), True),
        ((-4000, -1000), True),
    ]
    for move in moves:
        assert track.valid_move(start, move[0]) == move[1]
        start = move[0]


def test_cross_finish():
    from shapely import LineString

    track = Track("Austrian")
    finish_line_edge = list(zip(*track.finish_line.xy))[0]
    assert track.cross_finish_line((2000, -1000), (-1000, -2000)) == True
    assert track.cross_finish_line((-1000, -2000), (2000, -1000)) == True
    assert track.cross_finish_line((2000, -1000), finish_line_edge) == True
    assert track.cross_finish_line(finish_line_edge, (-1000, -2000)) == False
    assert track.cross_finish_line((2000, 0), (0, 0)) == False
    assert track.cross_finish_line(*list(zip(*track.finish_line.xy))) == False
    assert track.cross_finish_line(*reversed(list(zip(*track.finish_line.xy)))) == False

    assert track.cross_finish_line((2000, -1200), (0, -800)) == False
    point_x_1079 = Point(1079, -1409)
    point_x_1080 = Point(1080, -1409)
    assert track.cross_finish_line(point_x_1079, point_x_1080) == True


def test_contains():
    track = Track("Austrian")
    finish_line_edge = list(zip(*track.finish_line.xy))[0]
    assert track.contains((2000, -1000)) == True
    assert track.contains(Point(-1000, -2000)) == True
    assert track.contains(finish_line_edge) == True
    assert track.contains((0, 0)) == False
    assert track.contains(Point(2000, 0)) == False


def test_distance():
    track = Track("Austrian")
    accepted_precision = track.length * 0.0001
    start_point = track.starting_point
    assert track.get_distance(start_point) < accepted_precision
    point_2 = (-2000, -2000)
    dist = track.starting_point.distance(Point(point_2))
    assert abs(track.get_distance(point_2) - dist) < accepted_precision
    point_3 = Point(2000, -1000)
    dist = track.length - track.starting_point.distance(point_3)
    assert abs(track.get_distance(point_3) - dist) < accepted_precision

    with pytest.raises(ValueError):
        track.get_distance((0, 0))
