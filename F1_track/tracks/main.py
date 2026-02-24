# %matplotlib widget
import matplotlib.pyplot as plt
from .track import Track, get_all_tracks_by_year


if __name__ == "__main__":
    year = 2024
    for idx, track in enumerate(get_all_tracks_by_year(year)):
        track.save()
        fig, ax = track.plot()
        plt.savefig(f"F1_track/tracks/plots/{idx+1}_{track.name}.png")
        plt.show()
        plt.close()
        break

    # for idx, event in enumerate(sched.EventName):
    #     event_name = (" ").join(event.split(" ")[:-2])
    #     if event_name == "Japanese":
    #         continue

    #     track = Track(idx + 1, year=year, width=tracks_widths.get(event_name, 400))

    #     print("layout", track.finish_line.length)

    #     save_object(track)
    #     fig, ax = track.plot()
    #     plt.savefig(f"F1_track/tracks/plots/{idx+1}_{event_name}.png")
    #     plt.show()  # for some reason matplotlib backend does not work
    #     plt.close()
    #     # break

    # track = load_object("Bahrain.pkl")
    # fig, ax = track.plot()
    # plt.savefig(f"F1_track/tracks/plots/uuu.png")
