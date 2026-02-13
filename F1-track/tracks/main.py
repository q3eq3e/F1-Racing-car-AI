# %matplotlib widget
import matplotlib.pyplot as plt
from track import Track
import fastf1 as ff1

# add saving track objects to file
if __name__ == "__main__":
    year = 2024
    sched = ff1.get_event_schedule(year, include_testing=False)

    for idx, event in enumerate(sched.EventName):
        event_name = (" ").join(event.split(" ")[:-2])
        if event_name == "Japanese":
            continue
        # create a dict for every track with width and start line and rotation maybe and year(driver) to avoid bugs
        track = Track(idx + 1, year=year, width=200)

        fig, ax = track.plot()
        plt.savefig(f"F1-track/tracks/plots/{idx+1}_{event_name}.png")
        plt.show()  # for some reason matplotlib backend does not work
        # break

    # from shapely.geometry import LineString, Polygon, Point

    # p = Polygon(
    #     shell=[(0, 0), (1, 0), (2, 3), (5, 8), (-1, 5), (0, 0)],
    #     holes=[[(1, 1), (0, 4), (2, 5), (3, 6)]],
    # )
    # p = p.buffer(0.15)
    # x, y = p.exterior.xy
    # fig, ax = plt.subplots()
    # ax.fill(x, y, facecolor="grey", edgecolor="black")

    # # Cut holes
    # for interior in p.interiors:
    #     x, y = interior.xy
    #     ax.fill(x, y, facecolor="lightgreen", edgecolor="black")

    # ax.set_aspect("equal")

    # plt.savefig("aaa.png")
