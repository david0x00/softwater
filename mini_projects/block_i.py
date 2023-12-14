import numpy as np
import matplotlib.pyplot as plt

# Define the logo's vertices
logo_vertices = np.array([
    [0, 25],
    [3, 25],
    [3, 27],
    [1.5, 27],
    [1.5, 31],
    [3, 31],
    [3, 33],
    [-3, 33],
    [-3, 31],
    [-1.5, 31],
    [-1.5, 27],
    [-3, 27],
    [-3, 25],
    [0, 25]
])

logo_vertices = np.array([
    [0, 25],
    [-4, 29],
    [0, 33]
])

# Calculate the total length of the logo's perimeter
total_logo_length = np.sum(np.linalg.norm(np.diff(logo_vertices, axis=0), axis=1))

# Define the number of desired waypoints and calculate the step size
num_waypoints = 100
step_size = total_logo_length / num_waypoints

# Generate the waypoints along the perimeter
waypoints = []
current_distance = 0

for i in range(len(logo_vertices) - 1):
    start = logo_vertices[i]
    end = logo_vertices[i + 1]
    segment_length = np.linalg.norm(end - start)
    
    while current_distance + step_size < segment_length:
        t = (current_distance + step_size) / segment_length
        interpolated_point = (1 - t) * start + t * end
        waypoints.append(interpolated_point)
        current_distance += step_size

    current_distance -= segment_length

# Add the last vertex as a waypoint
waypoints.append(logo_vertices[-1])

# Extract x and y coordinates from the waypoints
waypoints = np.array(waypoints)
print(waypoints)
x_coords = waypoints[:, 0]
y_coords = waypoints[:, 1]

# Plot the logo trajectory
plt.figure(figsize=(8, 8))
plt.plot(x_coords, y_coords, marker='o', markersize=4, color='b', label='Logo Trajectory')
plt.plot(logo_vertices[:, 0], logo_vertices[:, 1], marker='o', markersize=6, color='r', linestyle='dashed', label='Logo Vertices')
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.title('University of Illinois Block "I" Logo Trajectory')
plt.legend()
plt.grid(True)
plt.axis('equal')
plt.show()
