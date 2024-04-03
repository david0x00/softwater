import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def draw_3d_frame(ax, pitch, roll, yaw):
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
    ax.quiver(0, 0, 0, x_axis[0], x_axis[1], x_axis[2], color='r', label='X')
    ax.quiver(0, 0, 0, y_axis[0], y_axis[1], y_axis[2], color='g', label='Y')
    ax.quiver(0, 0, 0, z_axis[0], z_axis[1], z_axis[2], color='b', label='Z')

    # Set equal aspect ratio
    ax.set_box_aspect([np.ptp(ax.get_xlim()), np.ptp(ax.get_ylim()), np.ptp(ax.get_zlim())])


# Example usage:
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Draw reference frame with pitch, roll, and yaw angles
pitch = 1.9  # 30 degrees
roll = 178.06   # 45 degrees
yaw = -126.12    # 60 degrees
draw_3d_frame(ax, pitch, roll, yaw)

# Set plot limits and labels
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_zlim(-1, 1)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

plt.legend()
plt.show()
