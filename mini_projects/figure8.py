import numpy as np
import matplotlib.pyplot as plt

def figure_eight(t):
    x = 5*np.sin(t)
    y = 5*np.sin(t)*np.cos(t) + 29
    return x, y

def length(x, y):
    return np.sqrt(np.diff(x)**2 + np.diff(y)**2).sum()

def generate_equal_length_waypoints(num_waypoints):
    t_values = np.linspace(0, 2*np.pi, 1000)
    x, y = figure_eight(t_values)
    total_length = length(x, y)
    segment_length = total_length / num_waypoints

    waypoints = [(x[0], y[0])]
    current_length = 0
    for i in range(1, len(t_values)):
        segment_len = length(x[:i+1], y[:i+1])
        if segment_len >= current_length + segment_length:
            waypoints.append((x[i], y[i]))
            current_length += segment_length
        if len(waypoints) == num_waypoints:
            break

    print(total_length, segment_length)
    return waypoints

# Number of waypoints
num_waypoints = 30

# Generate equal length waypoints
waypoints = generate_equal_length_waypoints(num_waypoints)

# Print waypoints
for i, (x, y) in enumerate(waypoints):
    print(f"Waypoint {i+1}: x={x:.3f}, y={y:.3f}")

# Plot the figure-8 trajectory and waypoints
t_values = np.linspace(0, 2*np.pi, 1000)
x, y = figure_eight(t_values)
plt.figure(figsize=(8, 6))
plt.plot(x, y, label="Figure-8 Trajectory")
plt.scatter(*zip(*waypoints), color='red', label="Waypoints")
plt.xlabel("X")
plt.ylabel("Y")
plt.title("Figure-8 Trajectory with Equal Length Waypoints")
plt.legend()
plt.grid(True)
plt.axis('equal')
plt.show()
