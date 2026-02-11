import requests

# import matplotlib

# matplotlib.use("TkAgg")  # or 'Qt5Agg'
# print(matplotlib.get_backend())
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


# Define a function to fetch car location data
def fetch_car_data(session_key, driver_number, start_time, end_time):
    # url = f"https://api.openf1.org/v1/location?session_key={session_key}&driver_number={driver_number}&date>{start_time}&date<{end_time}"
    upper_session_key = str(int(session_key) + 100)
    url = f"https://api.openf1.org/v1/location?session_key={session_key}&driver_number={driver_number}&date>{start_time}&date<{end_time}"
    response = requests.get(url)
    return response.json()


# Function to plot the path in 3D
def plot_car_path_3d(x_coords, y_coords, z_coords):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    ax.plot(
        x_coords, y_coords, z_coords, marker="o", color="b", linestyle="", markersize=5
    )
    ax.set_title("Car Path (3D Visualization)")
    ax.set_xlabel("X Coordinate (Latitude)")
    ax.set_ylabel("Y Coordinate (Longitude)")
    ax.set_zlabel("Z Coordinate (Altitude/Height)")

    plt.show()


# Modify the time window for multiple points
session_key = "9683"
driver_number = "16"
start_time = "2025-02-26T13:03:35.200"  # Start time (you can adjust to get more data)
end_time = "2025-02-26T14:03:35.800"  # End time (adjust the time for more data)

# Fetch the data
data = fetch_car_data(session_key, driver_number, start_time, end_time)
# leave only one per ten points
data2 = data
# data2 = [point for i, point in enumerate(data) if i % 100 == 0]
# Extract x, y, z coordinates from the data
x_coords = [
    point["x"] for point in data2 if point["z"] != 0
]  # x (latitude or X in some data)
y_coords = [point["y"] for point in data2 if point["z"] != 0]  # y (longitude or Y)
z_coords = [point["z"] for point in data2 if point["z"] != 0]  # z (altitude/height)

# x_coords = []
# y_coords = []
# z_coords = []

# for point in data:
#     if point["z"] != 0:
#         x_coords.append(point["x"])
#         y_coords.append(point["y"])
#         z_coords.append(point["z"])

# Plot the path in 3D
plot_car_path_3d(x_coords, y_coords, z_coords)
