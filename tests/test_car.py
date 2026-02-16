from F1_track.car import CarDynamics


def test_config():
    assert True == True


def test_car_init():
    CarDynamics()


def test_car_max_speed():
    car = CarDynamics()
    assert car.max_speed > 50 and car.max_speed < 500
