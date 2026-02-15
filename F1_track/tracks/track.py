from shapely.geometry import Polygon, LineString, Point
from typing import Tuple, List
from . import utils
import numpy as np
import fastf1 as ff1
import shapely
import matplotlib.pyplot as plt
import pickle


class Track:
    def __init__(
        self,
        idx: str | int,
        year: int = 2024,
        driver: str = None,
        width: int = 400,
        step=1,
    ) -> None:
        # idx could be a string name or integer
        # width 200 is closest to real world but 400 improves visibility
        session = ff1.get_session(year, idx, "Q")  # fastest lap from quali
        session.load()
        if driver is None:
            lap = session.laps.pick_fastest()
        else:
            lap = session.laps.pick_drivers(driver).pick_fastest()
        track_angle = session.get_circuit_info().rotation / 180 * np.pi

        x = lap.telemetry["X"][::step]  # values for x-axis
        y = lap.telemetry["Y"][::step]  # values for y-axis
        points_line = list(zip(x, y))
        points_line.append(points_line[0])  # closing a circuit loop
        points_line = utils.rotate(
            points_line, angle=track_angle
        )  # rotating for better view

        self.name = (" ").join(session.event.EventName.split(" ")[:-2])
        if self.name == "Japanese":
            raise ValueError("Not able to create Japanese track")

        self.length = shapely.length(LineString(points_line))

        self.layout: Polygon = LineString(points_line).buffer(width / 2)
        if len(self.layout.interiors) != 1:
            raise ValueError("Invalid width (present shortcuts)")

        self.finish_line = utils.get_finish_line(self.layout, points_line[0])
        self.starting_point = self.finish_line.centroid
        self.width = width
        # self._start_direction = (
        #     points_line[1][0] - points_line[0][0],
        #     points_line[1][1] - points_line[0][1],
        # )  # vector more or less perpendicular to finish_line

    @staticmethod
    def load(filename: str) -> "Track":
        with open(f"F1_track/tracks/saved/{filename}.pkl", "rb") as fp:
            return pickle.load(fp)

    def save(self: "Track", filename: str = None) -> None:
        if filename is None:
            filename = f"{self.name}.pkl"
        with open(f"F1_track/tracks/saved/{filename}", "wb") as fp:
            pickle.dump(self, fp, pickle.HIGHEST_PROTOCOL)

    def cross_finish_line(
        self,
        prev_point: Point | Tuple[float, float],
        next_point: Point | Tuple[float, float],
    ) -> bool:
        """checks if we properly cross a line in this step. So far enables crossing in both directions"""
        # add some heuristic later to make it faster e.g. if step length is smaller than distance to the edge

        if self.finish_line.contains(
            Point(prev_point)
        ) or self.finish_line.boundary.contains(
            Point(prev_point)
        ):  # could get rid of that boundary to speed up
            return False

        if self.finish_line.contains(
            Point(next_point)
        ) or self.finish_line.boundary.contains(Point(next_point)):
            return True

        return shapely.crosses(
            self.finish_line, LineString([prev_point, next_point])
        ) and self.valid_move(prev_point, next_point)

    def valid_move(
        self,
        prev_point: Point | Tuple[float, float],
        next_point: Point | Tuple[float, float],
    ) -> bool:
        """check if whole line is within track limits"""
        return self.layout.contains(LineString([prev_point, next_point]))

    def plot(self):
        fig, ax = plt.subplots()
        ax.set_facecolor("lightgreen")

        # Plot exterior
        x, y = self.layout.exterior.xy
        ax.fill(x, y, facecolor="grey", edgecolor="black")

        # Cut holes
        for interior in self.layout.interiors:
            x, y = interior.xy
            ax.fill(x, y, facecolor="lightgreen", edgecolor="black")

        ax.plot(*self.finish_line.xy, color="red", linewidth=2)

        ax.set_aspect("equal")
        return fig, ax


def get_all_tracks_by_year(year) -> List[Track]:
    tracks_widths = {
        "Saudi Arabian": 320,
        "Miami": 280,
        "Monaco": 140,
        "Canadian": 320,
        "Dutch": 360,
        "Azerbaijan": 80,
        "Singapore": 380,
        "São Paulo": 380,
    }

    sched = ff1.get_event_schedule(year, include_testing=False)
    tracks_list = []
    for idx, event in enumerate(sched.EventName):
        event_name = (" ").join(event.split(" ")[:-2])
        if event_name == "Japanese":
            continue

        tracks_list.append(
            Track(idx + 1, year=year, width=tracks_widths.get(event_name, 400))
        )

    return tracks_list


if __name__ == "__main__":
    import shapely
    from shapely.geometry import Point

    track = Track("Austria", width=120)

    print(track.layout.is_valid)
    print(shapely.is_valid_reason(track.layout))
    print(track.layout.contains(Point(0, 0)))
    print(track.layout.contains(Point(-2000, -2000)))
    print(track.layout.contains(Point(-2000, 0)))
