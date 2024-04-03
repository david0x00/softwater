import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

data_file = "/Users/davidnull/phd/3D Module/data/margins_data/new_data.csv"
data_file = "/Users/davidnull/phd/3D Module/data/margins_data/gripperAroundObstacle.csv"

df = pd.read_csv(data_file)
df["seconds"] = df["timestamp"] / 1000000
start_time = df["seconds"].iloc[0]
df["seconds"] = df["seconds"] - start_time
# dff = df.loc[df['stage'] == 6]
# dfr = df.loc[df['stage'] == 4]
# print(dff)
# print(dfr)
# df = df.reset_index(drop=True)

# stage_data = []
# for i in range(7):
#     dft = df.loc[df['stage'] == 6]
#     dft = df.reset_index(drop=True)
#     stage_data.append(dft.copy())


def draw_3d_frame(ax, pitch, roll, yaw, stage):
    """
    Draw a 3D reference frame in a 3D plot.

    Parameters:
        ax (matplotlib.axes._subplots.Axes3DSubplot): Axes object to draw on.
        pitch (float): Pitch angle in radians.
        roll (float): Roll angle in radians.
        yaw (float): Yaw angle in radians.
    """
    # Rotation matrices
    def rotation_x(theta):
        return np.array([
            [1, 0, 0],
            [0, np.cos(theta), -np.sin(theta)],
            [0, np.sin(theta), np.cos(theta)]
        ])

    def rotation_y(theta):
        return np.array([
            [np.cos(theta), 0, np.sin(theta)],
            [0, 1, 0],
            [-np.sin(theta), 0, np.cos(theta)]
        ])

    def rotation_z(theta):
        return np.array([
            [np.cos(theta), -np.sin(theta), 0],
            [np.sin(theta), np.cos(theta), 0],
            [0, 0, 1]
        ])

    # Rotate unit vectors
    x_axis = rotation_z(yaw) @ rotation_y(pitch) @ rotation_x(roll) @ np.array([[1, 0, 0]]).T
    y_axis = rotation_z(yaw) @ rotation_y(pitch) @ rotation_x(roll) @ np.array([[0, 1, 0]]).T
    z_axis = rotation_z(yaw) @ rotation_y(pitch) @ rotation_x(roll) @ np.array([[0, 0, 1]]).T

    # Plot reference frame
    ax.quiver(0, 0, stage, x_axis[0], x_axis[1], x_axis[2], color='r', arrow_length_ratio=0.1, label='X')
    ax.quiver(0, 0, stage, y_axis[0], y_axis[1], y_axis[2], color='g', arrow_length_ratio=0.1, label='Y')
    ax.quiver(0, 0, stage, z_axis[0], z_axis[1], z_axis[2], color='b', arrow_length_ratio=0.1, label='Z')

    # Set equal aspect ratio
    ax.set_box_aspect([np.ptp(ax.get_xlim()), np.ptp(ax.get_ylim()), np.ptp(ax.get_zlim())])

# Initialize the figure and axes
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

fps = 30

# Function to update the plot for animation
def update(frame):
    time_set = frame * (1 / fps)
    # print("start")
    ax.clear()  # Clear previous frame
    for i in range(7):
        dft = df.loc[df['stage'] == i]
        dft = dft.reset_index(drop=True)

        place_id = (dft['seconds']-time_set).abs().argsort()[0]

        pitch = dft["pitch"].iloc[place_id]
        roll = dft["roll"].iloc[place_id]
        yaw = dft["yaw"].iloc[place_id]
        # print(pitch, roll, yaw)

        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_zlim(-1, 8)
        draw_3d_frame(ax, pitch, roll, yaw, i)

# Create animation
ani = FuncAnimation(fig, update, frames=12000, interval=33)

plt.legend()
plt.show()
