from shapely.geometry import Polygon
from typing import Tuple
from utils import *
import fastf1 as ff1


class Track:
    def __init__(
        self,
        idx: str | int,
        year: int = 2024,
        driver: str = None,
        width: int = 100,
        step=1,
    ) -> None:
        # idx could be a string name or integer
        session = ff1.get_session(year, idx, "Q")  # fastest lap from quali
        session.load()
        if driver is None:
            lap = session.laps.pick_fastest()
        else:
            lap = session.laps.pick_drivers(driver).pick_fastest()
        track_angle = session.get_circuit_info().rotation / 180 * np.pi

        # removing last point bc is crossing finish line -- no longer needed
        # steps are to create more smooth track without sharp edges especially on the inside -- no longer needed
        x = lap.telemetry["X"][::step]  # values for x-axis
        y = lap.telemetry["Y"][::step]  # values for y-axis
        points_line = list(zip(x, y))
        points_line.append(points_line[0])  # closing a circuit loop
        points_line = rotate(points_line, angle=track_angle)  # rotating for better view
        # outer, inner = get_borders(x, y, width)
        # self.layout: Polygon = Polygon(shell=outer, holes=[inner])
        # self.outer: tuple = outer
        # self.inner: tuple = inner

        self.layout: Polygon = LineString(points_line).buffer(width)
        if len(self.layout.interiors) != 1:
            raise ValueError("Invalid width (present shortcuts)")

        self.finish_line = get_finish_line(self.layout, points_line[0])
        self.starting_point = self.finish_line.centroid
        self.width = width
        self.name = (" ").join(session.event.EventName.split(" ")[:-2])

    def cross_finish_line(
        self, prev_point: Tuple[float, float], next_point: Tuple[float, float]
    ) -> None:
        """checks if we cross a line in this step (we are close and change a side of a line with this step)"""
        accepted_distance = self.width // 2
        if change_side_of_line(
            prev_point,
            next_point,
            (self.finish_line.xy[0][0], self.finish_line.xy[1][0]),
            (self.finish_line.xy[0][1], self.finish_line.xy[1][1]),
        ):
            return self.finish_line.dwithin(Point(prev_point), accepted_distance)
        return False

    def valid_move(
        self, prev_point: Tuple[float, float], next_point: Tuple[float, float]
    ) -> None:
        """check if whole line is within track limits"""
        return self.layout.contains(LineString([prev_point, next_point]))

    def plot(self):
        import matplotlib.pyplot as plt

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


if __name__ == "__main__":
    import shapely
    from shapely.geometry import Point

    track = Track("Austria", width=120)

    print(track.layout.is_valid)
    print(
        shapely.is_valid_reason(track.layout)
    )  # usually not valid because of small intersections on the inside edge of a corner
    print(track.layout.contains(Point(0, 0)))
    print(track.layout.contains(Point(-2000, -2000)))
    print(track.layout.contains(Point(-2000, 0)))
