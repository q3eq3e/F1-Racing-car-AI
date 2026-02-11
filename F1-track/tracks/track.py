from shapely.geometry import Polygon
from typing import Tuple
from utils import get_borders
import fastf1 as ff1

# get-event_schedule


class Track:
    def __init__(self, name, year=2023, driver=None, width=100):
        session = ff1.get_session(year, name, "Q")  # fastest lap from quali
        session.load()
        if driver is None:
            lap = session.laps.pick_fastest()
        else:
            lap = session.laps.pick_drivers(driver).pick_fastest()

        # removing last point bc is crossing finish line
        x = lap.telemetry["X"][:-1]  # values for x-axis
        y = lap.telemetry["Y"][:-1]  # values for y-axis
        outer, inner = get_borders(x, y, width)

        self.layout: Polygon = Polygon(shell=outer, holes=[inner])
        self.layout: Polygon = Polygon(shell=self.layout.exterior.coords, holes=[inner])
        self.outer: tuple = outer
        self.inner: tuple = inner

    def plot(self):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()

        # Plot exterior
        x, y = self.layout.exterior.xy
        ax.fill(x, y, facecolor="grey", edgecolor="black")

        # Cut holes
        for interior in self.layout.interiors:
            x, y = interior.xy
            ax.fill(x, y, facecolor="white", edgecolor="black")

        ax.set_aspect("equal")
        return fig, ax


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import shapely
    from shapely.geometry import Point

    track = Track("Austria", width=200)

    print(track.layout.is_valid)
    print(
        shapely.is_valid_reason(track.layout)
    )  # usually not valid because of small intersections on the inside edge of a corner
    print(track.layout.contains(Point(0, 0)))
    print(track.layout.contains(Point(-2000, -2000)))
    print(track.layout.contains(Point(-2000, 0)))

    fig, ax = track.plot()
    plt.savefig("mygraph.png")
    plt.show()  # for some reason matplotlib backend does not work
