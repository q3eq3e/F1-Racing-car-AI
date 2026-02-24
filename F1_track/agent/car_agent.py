from typing import Optional
from ..tracks import Track
from ..car import CarDynamics
from .utils import Move

track_names_map = {
    "Saudi Arabia": "Saudi Arabian",
    "Australia": "Australian",
    "China": "Chinese",
    "Imola": "Emilia Romagna",
    "Canada": "Canadian",
    "Spain": "Spanish",
    "Austria": "Austrian",
    "Hungary": "Hungarian",
    "Belgium": "Belgian",
    "Netherlands": "Dutch",
    "Italy": "Italian",
    "US": "United States",
    "Mexico": "Mexico City",
    "Brazil": "São Paulo",
}


class CarAgent:
    def __init__(
        self,
        track_name: str,
        year: int = 2024,
        track_width: int = 40,
        car_params: Optional[dict] = None,
        time_delta=0.01,
    ) -> None:
        track_name = track_names_map.get(track_name, track_name)
        if year == 2024 and track_width == 40:
            self._track = Track.load(track_name)
        else:
            self._track = Track(idx=track_name, year=year, width=track_width)

        self._dynamics = CarDynamics(car_params)
        self.dt = time_delta
        self.reset()

    @property
    def observation(self) -> dict:
        # TODO: add more e.g. distance, track limits around him at different angles
        return self._dynamics.state

    @property
    def actions(self) -> dict:
        return self._dynamics.actions

    @property
    def simple_actions(self) -> dict:
        return self._dynamics.simple_actions

    def get_last_move(self) -> "Move":
        return self.last_move

    def get_info(self) -> dict:
        dist = self._track.get_distance(self._dynamics.get_position())
        if dist > 0.9 * self._track.length and not self.sector1_finished:
            dist = 0
        return {
            "time": self.time,
            "distance": dist,
            "percentage": dist / self._track.length,
        }

    def reset(self) -> None:
        self._dynamics.set_position(
            self._track.starting_point.x,
            self._track.starting_point.y,
            self._track.starting_angle,
        )
        self.sector1_finished = False
        self.sector2_finished = False
        self.lap_finished = False
        self.last_move = None
        self.time = 0

    def _check_finished_sectors(self, move: Move) -> None:
        if self._track.cross_sector1_line(move.prev, move.next):
            self.sector1_finished = True
        if (
            self._track.cross_sector2_line(move.prev, move.next)
            and self.sector1_finished
        ):
            self.sector2_finished = True
        if (
            self._track.cross_finish_line(move.prev, move.next)
            and self.sector1_finished
            and self.sector2_finished
        ):
            self.lap_finished = True

    def finished(self) -> bool:
        return self.lap_finished

    def is_on_track(self) -> bool:
        return self._track.contains((self.observation["x"], self.observation["y"]))

    def simple_step(self, throttle: float, steer: float):
        prev_point = self._dynamics.get_position()
        self._dynamics.simple_step(throttle, steer, self.dt)
        next_point = self._dynamics.get_position()
        self.last_move = Move(prev_point, next_point)

        self.time = round(self.time + self.dt, 3)
        self._check_finished_sectors(self.last_move)

    def step(self, throttle: float, brake: float, steer: float):
        prev_point = self._dynamics.get_position()
        self._dynamics.step(throttle, brake, steer, self.dt)
        next_point = self._dynamics.get_position()
        self.last_move = Move(prev_point, next_point)

        self.time = round(self.time + self.dt, 3)
        self._check_finished_sectors(self.last_move)

    # def _reward(self):
    #     if self.finished():
    #         return 1000
    #     if self.last_move is not None:
    #         penalty_cutting = int(
    #             not (self._track.valid_move(self.last_move.prev, self.last_move.next))
    #         )
    #     else:
    #         penalty_cutting = 0
    #     penalty_out_of_track = int(not (self.is_on_track())) * 100
    #     penalty_slide = 50 * int(self.observation["front_slide"]) + 30 * int(
    #         self.observation["rear_slide"]
    #     )
    #     reward = -penalty_cutting - penalty_out_of_track - penalty_slide
    #     reward += self.sector1_finished * 100
    #     reward += self.sector2_finished * 100
    #     reward += self.get_info()["percentage"] * 100
    #     reward += self.observation["vx"]
    #     return reward
