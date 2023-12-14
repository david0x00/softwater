import numpy as np
import matplotlib.pyplot as plt

def generate_circle_waypoints(center, radius, num_waypoints):
    waypoints = []
    for i in range(num_waypoints+1):
        angle = np.pi * i / num_waypoints / 2
        x = center[0] - 7 * np.sin(angle)
        y = center[1] - 5 * np.cos(angle)
        waypoints.append((x, y))
    # waypoints.append(waypoints[0])
    return waypoints

# Define circle parameters
center = (0, 29)  # Center of the circle
radius = 4       # Radius of the circle
num_waypoints = 200  # Number of waypoints

waypoints = generate_circle_waypoints(center, radius, num_waypoints)

# Print waypoints
for point in waypoints:
    print(point)

# Plot the circle and waypoints
circle = plt.Circle(center, radius, fill=False)
fig, ax = plt.subplots()
ax.add_artist(circle)
ax.plot(*zip(*waypoints), marker='o', color='r', linestyle='dashed')
plt.axis('equal')
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Circle Trajectory with Equal Length Waypoints')
plt.show()
