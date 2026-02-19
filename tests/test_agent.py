from F1_track.agent import CarAgent
import numpy as np


def test_config():
    assert True == True


def test_init_defalut():
    agent = CarAgent("Monaco")
    assert agent.observation["x"] < -950 and agent.observation["x"] > -1050
    assert agent.observation["y"] < 100 and agent.observation["y"] > 50
    assert agent.observation["yaw"] < np.pi / 2 and agent.observation["yaw"] > 0
    assert agent.observation["vx"] == 0
    assert abs(agent.get_info()["distance"]) < 1e-3
    assert agent.get_info()["time"] == 0
    assert abs(agent.get_info()["percentage"]) < 1e-3
    assert agent.sector1_finished == False
    assert agent.sector2_finished == False
    assert agent.lap_finished == False
    assert agent.last_move is None
    assert agent.successfully_done() == False


def test_big_distance_at_start():
    agent = CarAgent("Saudi Arabian")
    assert abs(agent.get_info()["distance"]) < 1e-3
    assert agent.get_info()["time"] == 0
    assert abs(agent.get_info()["percentage"]) < 1e-3
    assert agent.sector1_finished == False
    assert agent.sector2_finished == False
    assert agent.lap_finished == False
    assert agent.last_move is None
    assert agent.successfully_done() == False


def test_actions():
    agent = CarAgent("Monaco")
    assert len(agent.actions) == 3
    assert len(agent.simple_actions) == 2


def test_step():
    agent = CarAgent("Monaco")
    assert agent.observation["x"] == agent._track.starting_point.x
    agent.step(1, 0, 0)
    assert agent.observation["x"] != agent._track.starting_point.x
    assert agent.observation["y"] != agent._track.starting_point.y
    assert agent.observation["vx"] != 0
    assert agent.observation["vy"] == 0
    assert agent.sector1_finished == False
    assert agent.get_info()["time"] == agent.dt
    assert agent.get_info()["distance"] > 0
    assert agent.get_info()["percentage"] > 0


def test_simple_step():
    agent = CarAgent("Monaco", time_delta=0.01)
    assert agent.observation["x"] == agent._track.starting_point.x
    agent.simple_step(1, 0)
    assert agent.observation["x"] != agent._track.starting_point.x
    assert agent.observation["y"] != agent._track.starting_point.y
    assert agent.observation["vx"] != 0
    assert agent.observation["vy"] == 0
    assert agent.sector1_finished == False
    assert agent.get_info()["time"] == agent.dt
    assert agent.get_info()["distance"] > 0
    assert agent.get_info()["percentage"] > 0


def test_last_move():
    agent = CarAgent("Monaco")
    agent.step(1, 0, 0)
    move1 = agent.get_last_move()
    agent.step(1, 0, 0)
    move2 = agent.get_last_move()
    assert move1 is not None
    assert move2 is not None
    assert move2 != move1


def test_reset_basic():
    agent = CarAgent("Italian")
    assert agent.observation["x"] == agent._track.starting_point.x
    agent.simple_step(1, 0)
    assert agent.observation["x"] != agent._track.starting_point.x
    agent.reset()
    assert agent.observation["x"] == agent._track.starting_point.x
    assert agent.get_last_move() is None
    assert agent.get_info()["time"] == 0
    assert agent.get_info()["distance"] < 1e-5


def test_cross_sector1():
    agent = CarAgent("Mexico City")
    for _ in range(1760):
        agent.simple_step(1, 0)
    for _ in range(330):
        agent.simple_step(-0.1, -0.1)
    for _ in range(1000):
        agent.simple_step(-1, 0)
    for _ in range(1000):
        agent.simple_step(1, 0)
    for _ in range(1000):
        agent.simple_step(-1, 0)

    assert agent.sector1_finished == True
    assert agent.sector2_finished == False
    assert agent.lap_finished == False
    assert agent.successfully_done() == False


def test_invalid_cross_sector1():
    agent = CarAgent("Mexico City")
    for _ in range(1860):
        agent.simple_step(1, 0)
    for _ in range(330):
        agent.simple_step(-0.1, -0.1)
    for _ in range(1000):
        agent.simple_step(-1, 0)
    for _ in range(1000):
        agent.simple_step(1, 0)
    for _ in range(1000):
        agent.simple_step(-1, 0)

    assert agent.sector1_finished == False
    assert agent.sector2_finished == False
    assert agent.lap_finished == False
    assert agent.successfully_done() == False


# TODO: add test while completing whole lap and crossing finish line backwards or backwards and frontwards then
