import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

data_file = "/Users/davidnull/phd/3D Module/data/margins_data/new_data.csv"
df = pd.read_csv(data_file)

df["seconds"] = df["timestamp"] / 1000000
start_time = df["seconds"].iloc[0]
df["seconds"] = df["seconds"] - start_time

# # Number of points for each curve
# num_points = 100

# # Generate some random data for 6 curves
# np.random.seed(0)  # for reproducibility
# curves_data = []
# for _ in range(6):
#     curvature = np.random.uniform(0.5, 2.0)
#     amplitude = np.random.uniform(0.5, 2.0)
#     phase_shift = np.random.uniform(0, np.pi)
#     time = np.linspace(0, 4 * np.pi, num_points)
#     depth = amplitude * np.sin(curvature * time + phase_shift)
#     curves_data.append(depth)

# # Create a figure and axis
# fig, ax = plt.subplots()

# # Create line objects for each curve
# lines = [ax.plot([], [], lw=2)[0] for _ in range(len(curves_data))]

# # Initialize function for animation
# def init():
#     ax.set_xlim(0, 4 * np.pi)
#     ax.set_ylim(-3, 3)
#     ax.set_xlabel('Time')
#     ax.set_ylabel('Depth')
#     ax.set_title('Animated Plot with Time and Depth')
#     for line in lines:
#         line.set_data([], [])
#     return lines

# # Update function for animation
# def update(frame):
#     x = np.linspace(0, 4 * np.pi, num_points)
#     for i, line in enumerate(lines):
#         y = curves_data[i] * np.sin(frame * (i + 1) * 0.1)  # Modify the curves with time
#         line.set_data(x, y)
#     return lines

# # Create animation
# ani = FuncAnimation(fig, update, frames=np.linspace(0, 2 * np.pi, 200), init_func=init, blit=True)

# # Show the animation
# plt.show()
