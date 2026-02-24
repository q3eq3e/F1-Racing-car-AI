from F1_track.agent import CarAgent
import numpy as np


def test_config():
    assert True is True


def test_init_defalut():
    agent = CarAgent("Monaco")
    assert agent.observation["x"] < -950 and agent.observation["x"] > -1050
    assert agent.observation["y"] < 100 and agent.observation["y"] > 50
    assert agent.observation["yaw"] < np.pi / 2 and agent.observation["yaw"] > 0
    assert agent.observation["vx"] == 0
    assert abs(agent.get_info()["distance"]) < 1e-3
    assert agent.get_info()["time"] == 0
    assert abs(agent.get_info()["percentage"]) < 1e-3
    assert agent.sector1_finished is False
    assert agent.sector2_finished is False
    assert agent.lap_finished is False
    assert agent.last_move is None
    assert agent.finished() is False
    assert agent.is_on_track() is True


def test_big_distance_at_start():
    agent = CarAgent("Saudi Arabia")
    assert abs(agent.get_info()["distance"]) < 1e-3
    assert agent.get_info()["time"] == 0
    assert abs(agent.get_info()["percentage"]) < 1e-3
    assert agent.sector1_finished is False
    assert agent.sector2_finished is False
    assert agent.lap_finished is False
    assert agent.last_move is None
    assert agent.finished() is False


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
    assert agent.sector1_finished is False
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
    assert agent.sector1_finished is False
    assert agent.get_info()["time"] == agent.dt
    assert agent.get_info()["distance"] > 0
    assert agent.get_info()["percentage"] > 0


# def test_step_return():
#     agent = CarAgent("Monaco")
#     obs, reward, finished, _, info = agent.step(1, 0, 0)
#     assert obs == agent.observation
#     assert finished == agent.finished()
#     assert info == agent.get_info()
#     assert reward == agent._reward()


# def test_simple_step_return():
#     agent = CarAgent("Monaco")
#     obs, reward, finished, _, info = agent.simple_step(1, 0)
#     assert obs == agent.observation
#     assert finished == agent.finished()
#     assert info == agent.get_info()
#     assert reward == agent._reward()


# def test_reward():
#     agent = CarAgent("Monaco")
#     assert agent._reward() < 1e-6 and agent._reward() >= 0
#     agent.simple_step(1, 0)
#     assert agent._reward() < -29 and agent._reward() > -61
#     for _ in range(200):
#         agent.simple_step(1, 0)
#     assert agent._reward() > 20
#     for _ in range(100):
#         agent.simple_step(1, -1)
#     assert agent._reward() > 20


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

    assert agent.sector1_finished is True
    assert agent.sector2_finished is False
    assert agent.lap_finished is False
    assert agent.finished() is False


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

    assert agent.sector1_finished is False
    assert agent.sector2_finished is False
    assert agent.lap_finished is False
    assert agent.finished() is False


def test_cross_sector2():
    agent = CarAgent("Mexico City")
    for _ in range(1760):
        agent.simple_step(1, 0)
    for _ in range(330):
        agent.simple_step(-0.1, -0.1)
    for _ in range(1000):
        agent.simple_step(-1, 0)
    for _ in range(1170):
        agent.simple_step(1, 0)
    # for _ in range(1000):
    #     agent.simple_step(-1, 0)
    for _ in range(330):
        agent.simple_step(-0.1, -0.1)
    for _ in range(1000):
        agent.simple_step(-1, 0)
    for _ in range(1050):
        agent.simple_step(1, 0)

    assert agent.sector1_finished is True
    assert agent.sector2_finished is True
    assert agent.lap_finished is False
    assert agent.finished() is False


def test_complete_lap():
    agent = CarAgent("Mexico City")
    for _ in range(1760):
        agent.simple_step(1, 0)
    for _ in range(330):
        agent.simple_step(-0.1, -0.1)
    for _ in range(1000):
        agent.simple_step(-1, 0)
    for _ in range(1170):
        agent.simple_step(1, 0)
    for _ in range(330):
        agent.simple_step(-0.1, -0.1)
    for _ in range(1000):
        agent.simple_step(-1, 0)
    for _ in range(1050):
        agent.simple_step(1, 0)

    for _ in range(150):
        agent.simple_step(-0.1, 0.1)
    for _ in range(550):
        agent.simple_step(1, 0)
    for _ in range(900):
        agent.simple_step(-0.1, -0.06)
    for _ in range(211):
        agent.simple_step(1, 0)

    assert agent.sector1_finished is True
    assert agent.sector2_finished is True
    assert agent.lap_finished is True
    assert agent.finished() is True
    assert agent.get_info()["time"] > 60
    assert agent.get_info()["distance"] < 1


def test_cross_line_backwards():
    agent = CarAgent("Mexico City")
    crossed_finish_line = False
    for _ in range(200):
        agent.simple_step(1, 0)
    for _ in range(300):
        agent.simple_step(0.0, 1)
    assert agent.is_on_track() is False
    for _ in range(270):
        agent.simple_step(0.0, 1)
        if agent._track.cross_finish_line(
            agent.get_last_move().prev, agent.get_last_move().next
        ):
            crossed_finish_line = True

    assert crossed_finish_line is True
    assert agent.sector1_finished is False
    assert agent.sector2_finished is False
    assert agent.lap_finished is False
    assert agent.finished() is False
    assert agent.get_info()["distance"] < 10
