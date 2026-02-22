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
    assert track.length > 4000 and track.length < 4500
    assert track.name == "Austrian"
    assert track.width == 40
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
    assert track.finish_line.centroid.distance(track.starting_point) < 1e-10
    assert track.starting_angle > -2.9 and track.starting_angle < -2.8


def test_change_width():
    track1 = Track("Austrian")
    track2 = Track("Austrian", width=10)
    assert track2.layout.is_valid
    assert len(track2.layout.interiors) == 1
    assert track2.width == 10
    assert track1.length == track2.length


def test_different_years():
    track1 = Track("Abu Dhabi", year=2024)
    track2 = Track("Abu Dhabi", year=2019)
    assert track1.length != track2.length
    assert abs(track1.length - track2.length) > 10


def test_too_wide():
    with pytest.raises(ValueError):
        Track("British", width=100)


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
        ((-200, -200), True),
        ((-200, -200), True),
        ((-190, -200), True),
        (Point(-190, -199), True),
        ((-200, -100), False),
        ((-200, -100), False),
        ((-300, -100), False),
        (Point(-300, -100), False),
        ((-500, -100), False),
        ((-400, -100), False),
        ((-200, -200), False),
        ((-250, -230), True),
        ((-330, -200), True),
        ((-400, -100), True),
    ]
    for move in moves:
        assert track.valid_move(start, move[0]) == move[1]
        start = move[0]


def test_cross_finish():
    track = Track("Austrian")
    finish_line_edge = list(zip(*track.finish_line.xy))[0]
    assert track.cross_finish_line((200, -100), (-100, -200)) == True
    assert track.cross_finish_line((-100, -200), (200, -100)) == True
    assert track.cross_finish_line((200, -100), finish_line_edge) == True
    assert track.cross_finish_line(finish_line_edge, (-100, -200)) == False
    assert track.cross_finish_line((200, 0), (0, 0)) == False
    assert track.cross_finish_line(*list(zip(*track.finish_line.xy))) == False
    assert track.cross_finish_line(*reversed(list(zip(*track.finish_line.xy)))) == False

    assert track.cross_finish_line((200, -120), (0, -80)) == False
    point_x_107 = Point(107, -140)
    point_x_108 = Point(108, -140)
    assert track.cross_finish_line(point_x_107, point_x_108) == True


def test_cross_sectors():
    track = Track("Austrian")
    assert track.cross_sector1_line((200, -100), (-100, -200)) == False
    assert track.cross_sector1_line((-800, 550), (-700, 550)) == True
    assert track.cross_sector1_line((-700, 550), (-800, 550)) == True

    assert track.cross_sector2_line((200, -100), (-100, -200)) == False
    assert track.cross_sector2_line((-480, 300), (-470, 200)) == True
    assert track.cross_sector2_line((-470, 200), (-480, 300)) == True


# def test_only_one_way_cross():
#     # not sure if needed when we have sector lines
#     track = Track("Austrian")
#     assert track.cross_finish_line((200, -100), (-100, -200)) == True
#     assert track.cross_finish_line((-100, -200), (200, -100)) == False

#     assert track.cross_sector1_line((-800, 550), (-700, 550)) == True
#     assert track.cross_sector1_line((-700, 550), (-800, 550)) == False

#     assert track.cross_sector2_line((-480, 300), (-470, 200)) == True
#     assert track.cross_sector2_line((-470, 200), (-480, 300)) == False


def test_contains():
    track = Track("Austrian")
    finish_line_edge = list(zip(*track.finish_line.xy))[0]
    assert track.contains((200, -100)) == True
    assert track.contains(Point(-100, -200)) == True
    assert track.contains(finish_line_edge) == True
    assert track.contains((0, 0)) == False
    assert track.contains(Point(200, 0)) == False


def test_distance():
    track = Track("Austrian")
    accepted_precision = track.length * 0.0001
    dist = track.get_distance(track.starting_point)
    assert min(dist, track.length - dist) < accepted_precision
    point_2 = (-200, -200)
    dist = track.starting_point.distance(Point(point_2))
    assert abs(track.get_distance(point_2) - dist) < accepted_precision
    point_3 = Point(200, -100)
    dist = track.length - track.starting_point.distance(point_3)
    assert abs(track.get_distance(point_3) - dist) < accepted_precision

    with pytest.raises(ValueError):
        track.get_distance((0, 0))
