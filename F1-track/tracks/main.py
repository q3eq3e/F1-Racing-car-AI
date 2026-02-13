# %matplotlib widget
import matplotlib.pyplot as plt
from track import Track
import fastf1 as ff1
import pickle

#  TODO tests


def save_object(obj, filename=None):
    if filename is None:
        filename = f"{obj.name}.pkl"
    with open(f"F1-track/tracks/saved/{filename}", "wb") as fp:
        pickle.dump(obj, fp, pickle.HIGHEST_PROTOCOL)


def load_object(filename):
    with open(f"F1-track/tracks/saved/{filename}", "rb") as fp:
        return pickle.load(fp)


tracks_widths = {
    "Saudi Arabian": 160,
    "Miami": 140,
    "Monaco": 70,
    "Canadian": 160,
    "Dutch": 180,
    "Azerbaijan": 40,
    "Singapore": 190,
    "São Paulo": 190,
}

if __name__ == "__main__":
    year = 2024
    sched = ff1.get_event_schedule(year, include_testing=False)

    for idx, event in enumerate(sched.EventName):
        event_name = (" ").join(event.split(" ")[:-2])
        if event_name == "Japanese":
            continue

        track = Track(idx + 1, year=year, width=tracks_widths.get(event_name, 200))

        save_object(track)
        fig, ax = track.plot()
        plt.savefig(f"F1-track/tracks/plots/{idx+1}_{event_name}.png")
        plt.show()  # for some reason matplotlib backend does not work
        plt.close()
        # break

    # track = load_object("Bahrain.pkl")
    # fig, ax = track.plot()
    # plt.savefig(f"F1-track/tracks/plots/uuu.png")

    # -----------------------

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
