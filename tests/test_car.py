from F1_track.car import CarDynamics
import pytest


def test_config():
    assert True == True


def test_car_init():
    car = CarDynamics()
    for key in car.state:
        assert car.state[key] == 0.0


def test_car_max_speed():
    car = CarDynamics()
    assert car.max_speed > 50 and car.max_speed < 150
    assert car.max_speed_kmh > 180 and car.max_speed_kmh < 540


def test_straight_move():
    car = CarDynamics()

    # start phase
    for _ in range(10):
        car.step(1, 0, 0, 0.05)

    for key in car.state:
        match key:
            case "x":
                assert car.state[key] > 0 and car.state[key] < 100
            case "vx":
                assert car.state[key] > 0 and car.state[key] < 30
            case "ax":
                assert car.state[key] > 5 and car.state[key] < 15
            case "rear_slide":
                assert car.state[key] == True
            case _:
                assert car.state[key] == 0.0

    # mid phase
    for _ in range(100):
        car.step(1, 0, 0, 0.05)

    for key in car.state:
        match key:
            case "x":
                assert car.state[key] > 100 and car.state[key] < 500
            case "vx":
                assert car.state[key] > 30 and car.state[key] < 100
            case "ax":
                assert car.state[key] > 0 and car.state[key] < 10
            case _:
                assert car.state[key] == 0.0

    # end phase
    for _ in range(1000):
        car.step(1, 0, 0, 0.05)

    for key in car.state:
        match key:
            case "x":
                assert car.state[key] > 1000 and car.state[key] < 5000
            case "vx":
                assert car.state[key] > 80 and car.state[key] <= car.max_speed
            case "ax":
                assert car.state[key] > 0 and car.state[key] < 2
            case _:
                assert car.state[key] == 0.0


def test_standing_braking_turning():
    car = CarDynamics()

    car.step(0, 0.5, 0)
    for key in car.state:
        assert car.state[key] == 0.0
    car.step(0, 1, 0)
    for key in car.state:
        assert car.state[key] == 0.0
    car.step(0, 0, 0.5)
    for key in car.state:
        assert car.state[key] == 0.0
    car.step(0, 0, -1)
    for key in car.state:
        assert car.state[key] == 0.0
    car.step(0, 1, 1)
    for key in car.state:
        assert car.state[key] == 0.0


def test_losing_grip():
    car = CarDynamics()

    for _ in range(1000):
        car.step(1, 0, 0)

    car.step(0, 0, 0)
    assert car.state["front_slide"] == False
    assert car.state["rear_slide"] == False
    car.step(0, 0, 1)
    assert car.state["front_slide"] == True
    assert car.state["rear_slide"] == False
    car.step(0, 0, 0.01)
    assert car.state["front_slide"] == False
    assert car.state["rear_slide"] == False
    for _ in range(1000):
        car.step(1, 0, 0)
    car.step(0, 0, -0.01)
    assert car.state["front_slide"] == False
    assert car.state["rear_slide"] == False
    car.step(0, 0, -1)
    assert car.state["front_slide"] == True
    assert car.state["rear_slide"] == False
    car.step(0, 0, 0)
    assert car.state["front_slide"] == False
    assert car.state["rear_slide"] == False


def test_out_of_range():
    car = CarDynamics()
    with pytest.raises(ValueError):
        car.step(2, 0, 0)
    with pytest.raises(ValueError):
        car.step(-0.5, 0, 0)
    with pytest.raises(ValueError):
        car.step(0, -0.5, 0)
    with pytest.raises(ValueError):
        car.step(0, 5, 0)
    with pytest.raises(ValueError):
        car.step(0, 0, -2)
    with pytest.raises(ValueError):
        car.step(0, 0, 1.2)


def test_fast_cornering():
    car = CarDynamics()
    for _ in range(1000):
        car.step(1, 0, 0)

    car.step(1, 0, 0.1)
    car.step(1, 0, 0.1)
    car.step(1, 0, 0.1)
    for key in car.state:
        match key:
            case "x":
                assert car.state[key] > 0
            case "y":
                assert car.state[key] > 0
            case "vy":
                assert car.state[key] < 0
            case "yaw":
                assert car.state[key] > 0
            case "yaw_rate":
                assert car.state[key] > 0
            case "front_slide":
                assert car.state[key] == False
            case "rear_slide":
                assert car.state[key] == False
            case _:
                pass

    for _ in range(1000):
        car.step(1, 0, 0)

    for key in car.state:
        match key:
            case "x":
                assert car.state[key] > 0
            case "y":
                assert car.state[key] > 0
            case "vy":
                assert abs(car.state[key]) < 1e-6
            case "yaw":
                assert car.state[key] > 0
            case "yaw_rate":
                assert abs(car.state[key]) < 1e-6
            case "front_slide":
                assert car.state[key] == False
            case "rear_slide":
                assert car.state[key] == False
            case _:
                pass

    car.step(1, 0, -0.1)
    car.step(1, 0, -0.1)
    car.step(1, 0, -0.1)
    for key in car.state:
        match key:
            case "x":
                assert car.state[key] > 0
            case "y":
                assert car.state[key] > 0
            case "vy":
                assert car.state[key] > 0
            case "yaw":
                assert abs(car.state[key]) < 1e-1
            case "yaw_rate":
                assert car.state[key] < 0
            case "front_slide":
                assert car.state[key] == False
            case "rear_slide":
                assert car.state[key] == False
            case _:
                pass

    for _ in range(1000):
        car.step(1, 0, 0)

    for key in car.state:
        match key:
            case "x":
                assert car.state[key] > 0
            case "y":
                assert car.state[key] > 0
            case "vy":
                assert abs(car.state[key]) < 1e-6
            case "yaw":
                assert abs(car.state[key]) < 1e-6
            case "yaw_rate":
                assert abs(car.state[key]) < 1e-6
            case "front_slide":
                assert car.state[key] == False
            case "rear_slide":
                assert car.state[key] == False
            case _:
                pass
