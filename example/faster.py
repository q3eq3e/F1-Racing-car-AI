import matplotlib as mpl
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from shapely import Polygon

import fastf1 as ff1

year = 2021
wknd = 9
ses = "R"
driver = "RIC"
colormap = mpl.cm.plasma

session = ff1.get_session(year, wknd, ses)
weekend = session.event
session.load()
lap = session.laps.pick_drivers(driver).pick_fastest()

# Get telemetry data
x = lap.telemetry["X"]  # values for x-axis
y = lap.telemetry["Y"]  # values for y-axis
color = lap.telemetry["Speed"]  # value to base color gradient on


def plot_car_path_2d(x_coords, y_coords):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)

    ax.plot(x_coords, y_coords, marker="o", color="b", linestyle="", markersize=5)
    ax.set_title("Car Path (2D Visualization)")
    ax.set_xlabel("X Coordinate (Latitude)")
    ax.set_ylabel("Y Coordinate (Longitude)")

    plt.show()


x2 = [point for i, point in enumerate(x) if i % 1 == 0]
y2 = [point for i, point in enumerate(y) if i % 1 == 0]
coords = tuple(zip(x2, y2))
polygon = Polygon(coords)
print(polygon.area)
# remove last point bc its crossing starting line
plot_car_path_2d(x2, y2)
pass
