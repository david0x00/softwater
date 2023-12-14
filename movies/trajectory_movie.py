import csv
import cv2
import numpy as np
import glob
import math
import pickle
import os
import pandas as pd
from detect import RobotDetector

traj_dir = "/Users/davidnull/phd/data/Trajectories/"
dir_name = "trpo_arc_down_left_100"

left=True
right = not left
up = False
down = not up

radius = 5
red = (0, 0, 255)
green = (0, 255, 0)
orange = (0, 165, 255)
yellow = (0, 255, 255)
blue = (255, 0, 0)
white = (255, 255, 255)
black = (0, 0, 0)

mtx = np.array([
    [1142.77, 0, 920.91],
    [0, 1138.46, 545.01],
    [0, 0, 1]
])

newcameramtx = np.array([
    [1135.68, 0, 919.23],
    [0, 1132.81, 543.06],
    [0, 0, 1]
])

inv_camera_mtx = np.linalg.inv(newcameramtx)

dist = np.array([[ 0.20121649, -0.49210822, -0.00094167, -0.00054018, 0.29212259]])

camera_to_markers_dist = 78.5 #cm

class Arc:
    num_waypoints = 100

    def __init__(self, left=False, right=False, up=False, down=False):
        if left is True:
            if up is True:
                self.center = (-7, 24)
                xc = 7
                yc = 5
                xf = np.cos
                yf = np.sin
            elif down is True:
                self.center = (0, 29)
                xc = -7
                yc = -5
                xf = np.sin
                yf = np.cos
        if right is True:
            if up is True:
                self.center = (7, 24)
                xc = -7
                yc = 5
                xf = np.cos
                yf = np.sin
            elif down is True:
                self.center = (0, 29)
                xc = 7
                yc = -5
                xf = np.sin
                yf = np.cos
         
        waypoints = []
        for i in range(self.num_waypoints+1):
            angle = np.pi * i / self.num_waypoints / 2
            x = self.center[0] + xc * xf(angle)
            y = self.center[1] + yc * yf(angle)
            waypoints.append((x, y))
        # waypoints.append(waypoints[0])
        self.waypoints = np.array(waypoints)
    
    def get_waypoints(self):
        return self.waypoints

class Circle:
    center = (0, 29)
    radius = 4
    num_waypoints = 500

    def __init__(self):
        waypoints = []
        for i in range(self.num_waypoints):
            angle = 2 * np.pi * i / self.num_waypoints
            x = self.center[0] - self.radius * np.sin(angle)
            y = self.center[1] - self.radius * np.cos(angle)
            waypoints.append((x, y))
        waypoints.append(waypoints[0])
        self.waypoints = np.array(waypoints)
    
    def get_waypoints(self):
        return self.waypoints

class BlockI:
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

    num_waypoints = 500

    def __init__(self):
        # Calculate the total length of the logo's perimeter
        total_logo_length = np.sum(np.linalg.norm(np.diff(self.logo_vertices, axis=0), axis=1))
    
        # Define the number of desired waypoints and calculate the step size
        step_size = total_logo_length / self.num_waypoints
    
        # Generate the waypoints along the perimeter
        self.waypoints = []
        current_distance = 0
        for i in range(len(self.logo_vertices) - 1):
            start = self.logo_vertices[i]
            end = self.logo_vertices[i + 1]
            segment_length = np.linalg.norm(end - start)

            while current_distance + step_size < segment_length:
                t = (current_distance + step_size) / segment_length
                interpolated_point = (1 - t) * start + t * end
                self.waypoints.append(interpolated_point)
                current_distance += step_size

            current_distance -= segment_length

        # Add the last vertex as a waypoint
        self.waypoints.append(self.logo_vertices[-1])

        # Extract x and y coordinates from the waypoints
        self.waypoints = np.array(self.waypoints)
    
    def get_waypoints(self):
        return self.waypoints

class TrajGenerator:
    def __init__(self):
        pass

    def figure_eight(self, t):
        x = 5*np.sin(t)
        y = 5*np.sin(t)*np.cos(t) + 29
        return x, y

    def length(self, x, y):
        return np.sqrt(np.diff(x)**2 + np.diff(y)**2).sum()

    def generate_equal_length_waypoints(self, num_waypoints):
        t_values = np.linspace(0, 2*np.pi, 1000)
        x, y = self.figure_eight(t_values)
        total_length = self.length(x, y)
        segment_length = total_length / num_waypoints

        waypoints = [(x[0], y[0])]
        current_length = 0
        for i in range(1, len(t_values)):
            segment_len = self.length(x[:i+1], y[:i+1])
            if segment_len >= current_length + segment_length:
                waypoints.append((x[i], y[i]))
                current_length += segment_length
            if len(waypoints) == num_waypoints:
                break
        print('Lengths')
        print(total_length, segment_length)
        return waypoints

def world2pix(x, y):
        coord_3d = np.array([
            x / camera_to_markers_dist,
            y / camera_to_markers_dist,
            1
        ])
        coord_2d = np.matmul(newcameramtx, coord_3d)
        return int(coord_2d[0]), int(coord_2d[1])

def draw_prev_path(img, path, orig, color):
    ox = orig[0]
    oy = orig[1]
    pathx = path[0]
    pathy = path[1]
    for i in range(1, len(pathx)):
        pathx[i-1] = float(pathx[i-1])
        pathy[i-1] = float(pathy[i-1])
        pathx[i] = float(pathx[i])
        pathy[i] = float(pathy[i])
        p1x = ox + pathx[i-1]
        p1y = oy - pathy[i-1]
        p1 = world2pix(p1x, p1y)
        p2x = ox + pathx[i]
        p2y = oy - pathy[i]
        p2 = world2pix(p2x, p2y)
        cv2.line(img, p1, p2, color, thickness=3)

    p1x = ox + pathx[0]
    p1y = oy - pathy[0]
    p1 = world2pix(p1x, p1y)
    p2x = ox + pathx[-1]
    p2y = oy - pathy[-1]
    p2 = world2pix(p2x, p2y)
    
    cv2.circle(img, p1, 5, color, 3)
    cv2.circle(img, p2, 5, color, 3)

def create_video(out):
    run_dir = traj_dir + dir_name + "/"
    csv_file = run_dir + "control_data_-9_25.csv"
    imgs_dir = run_dir + "imgs"
    df = pd.read_csv(csv_file)

    xee_prev = []
    vs_path = [[],[]]

    for idx, filename in enumerate(sorted(glob.glob(imgs_dir + '/*.jpg'), key=os.path.getmtime)):
        print(filename)
        img = cv2.imread(filename)
        oxw = df.iloc[idx]["ORIGX"]
        oyw = df.iloc[idx]["ORIGY"]
        origin = (oxw, oyw)
        # for i in range(1,10):
        #     mx = oxw + df.iloc[idx]["M" + str(i) + "X"]
        #     my = oyw - df.iloc[idx]["M" + str(i) + "Y"]
        #     m = world2pix(mx, my)
        #     cv2.circle(img, m, radius, blue, 3)

        xw = oxw + df.iloc[idx]["XEEX"]
        yw = oyw - df.iloc[idx]["XEEY"]
        tx = oxw + df.iloc[idx]["WAYX"]
        ty = oyw - df.iloc[idx]["WAYY"]
        tw = (tx, ty)

        # t_values = np.linspace(0, 2*np.pi, 1000)
        # x, y = TrajGenerator().figure_eight(t_values)

        # wp = Circle().get_waypoints()
        wp = Arc(left=left, right=right, up=up, down=down).get_waypoints()
        x = wp[:,0]
        y = wp[:,1]

        for index, x_val in enumerate(x):
            new_x = oxw + x[index]
            new_y = oyw - y[index] 
            point = world2pix(new_x, new_y)
            if index == 0:
                point_prev = point
            else:
                cv2.line(img, point_prev, point, black, thickness=1)
                point_prev = point

        vs_path[0].append(df.iloc[idx]["XEEX"])
        vs_path[1].append(df.iloc[idx]["XEEY"])

        xee = world2pix(xw, yw)
        orig = world2pix(oxw, oyw)
        targ = world2pix(tx, ty)

        for j in range(len(xee_prev)):
            if j == 0:
                cv2.circle(img, xee_prev[j], radius, green, 3)
            p1 = xee_prev[j]
            if j < len(xee_prev)-1:
                p2 = xee_prev[j+1]
            else:
                p2 = xee
            cv2.line(img, p1, p2, green, thickness=3)
        xee_prev.append(xee)

        cv2.circle(img, targ, radius, red, 3)
        cv2.circle(img, xee, radius, green, 3)

        out.write(img)

if __name__ == "__main__":
    mp4_codec = cv2.VideoWriter_fourcc(*'X264')
    avi_codec = cv2.VideoWriter_fourcc(*'DIVX')

    size = (1920, 1080)

    hz = 2
    speed = 4
    fps = speed * hz

    proj_dir = traj_dir
    proj_name = dir_name
    proj_ext = ".mp4"
    file_name = proj_dir + proj_name + proj_ext

    out = cv2.VideoWriter(file_name, mp4_codec, fps, size)

    create_video(out)

    out.release()
