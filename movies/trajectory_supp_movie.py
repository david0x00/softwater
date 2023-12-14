import csv
import cv2
import numpy as np
import glob
import math
import pickle
import os
import pandas as pd
from detect import RobotDetector

radius = 5
red = (0, 0, 255)
green = (0, 255, 0)
orange = (0, 165, 255)
yellow = (0, 255, 255)
blue = (255, 0, 0)
white = (255, 255, 255)
black = (0, 0, 0)
light_green = (144, 238, 144)
dark_green = (0, 150, 0)
light_blue = (211, 156, 75)
blue = (150, 0, 0)

traj_dir = "/Users/davidnull/phd/data/Trajectories/final_trajectories/"
dir_name = "traj_supp_vid_temp"

controllers = ["olik", "vs", "cql", "trpo", "ampc"]
controller_names = ["Open Loop IK", "Visual Servo", "CQL", "TRPO", "AutoMPC"]
controller_colors = [light_blue, blue, light_green, dark_green, red]

controller_errors = [[],[],[],[],[]]

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

def world2pix(x, y):
    coord_3d = np.array([
        x / camera_to_markers_dist,
        y / camera_to_markers_dist,
        1
    ])
    coord_2d = np.matmul(newcameramtx, coord_3d)
    return int(coord_2d[0]), int(coord_2d[1])

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
    
def draw_path(img, xee_prev, color):
    for j in range(len(xee_prev)):
        if j == 0:
            cv2.circle(img, xee_prev[j], radius, color, 3)
        if j < len(xee_prev)-1:
            p1 = xee_prev[j]
            p2 = xee_prev[j+1]
            cv2.line(img, p1, p2, color, thickness=3)

def zoom_at(img, zoom=1, angle=0, coord=None):
    
    cy, cx = [ i/2 for i in img.shape[:-1] ] if coord is None else coord[::-1]
    
    rot_mat = cv2.getRotationMatrix2D((cx,cy), angle, zoom)
    result = cv2.warpAffine(img, rot_mat, img.shape[1::-1], flags=cv2.INTER_LINEAR)
    
    return result

def add_pressure_box(img, df, idx):
    ptop = 324
    pbot = 1080
    pleft = 1478
    pright = 1920
    pwidth = pright - pleft
    plength = pbot - ptop
    xpad = 80
    ypad = 20
    
    pbox_full_p1 = (pleft, ptop)
    pbox_full_p2 = (pright, pbot)
    cv2.rectangle(img, pbox_full_p1, pbox_full_p2, white, -1)
    cv2.rectangle(img, pbox_full_p1, pbox_full_p2, black, 1)
    ptitle_p1 = (pleft, ptop-30)
    ptitle_p2 = (pright, ptop)
    cv2.rectangle(img, ptitle_p1, ptitle_p2, white, -1)
    cv2.rectangle(img, ptitle_p1, ptitle_p2, black, 1)

    text = "Internal Pressures (kPa)"
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 0.7
    thickness = 2
    ptitle_p = (pleft + 10, ptop - 7)
    cv2.putText(img, text, ptitle_p, font, fontScale, black, thickness)

    pressures = [
        [df.iloc[idx]["M2-PL"], df.iloc[idx]["M1-PL"]],
        [df.iloc[idx]["M2-PR"], df.iloc[idx]["M1-PR"]]
    ]

    max_pressure = 120
    min_pressure = 98
    del_pressure = max_pressure - min_pressure

    for i in range(2):
        for j in range(2):
            width = int(pwidth / 2)
            length = int(plength / 2)
            off_x = pleft + (i * width)
            off_y = ptop + (j * length)
            pbox_top = off_y + ypad
            pbox_bot = off_y + length - ypad
            pbox_left = off_x + xpad 
            pbox_right = off_x + width - int(xpad / 1)
            pbox_p1 = (pbox_left, pbox_top)
            pbox_p2 = (pbox_right, pbox_bot)

            pb_length = pbox_bot - pbox_top
            
            ap_val = pressures[i][j]
            ap_val_x = pbox_left - 50

            ap_top = pbox_bot - int(pb_length * ((ap_val - min_pressure) / del_pressure))
            ap_p1 = (pbox_left, ap_top)
            ap_p2 = (pbox_right, pbox_bot)

            ap_val_p = (ap_val_x, ap_top)

            ap_text = str(round(ap_val, 1))
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 0.5
            thickness = 2

            cv2.rectangle(img, ap_p1, ap_p2, blue, -1)
            cv2.putText(img, ap_text, ap_val_p, font, fontScale, blue, thickness)
            cv2.rectangle(img, pbox_p1, pbox_p2, black, 3)

def add_title_box(img, name, color):
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 0.6
    thickness = 2
    dp_x = 15
    dp_y = 45
    dp_del = 40
    fontScale = 1
    cv2.rectangle(img, (0,0), (250,110), white, -1)
    cv2.rectangle(img, (100,67), (200,83), color, -1)
    cv2.rectangle(img, (100,67), (200,83), black, 1)
    title = [name, "4x"]
    for i, text in enumerate(title):
        details_p = (dp_x, dp_y + (dp_del * i)) 
        color = black
        cv2.putText(img, text, details_p, font, fontScale, color, thickness)

def add_text(img, distance, xee, targ, color):
    details = []
    details.append("Dist Error (cm): " + str(distance))
    details.append("Xee (cm):       " + str(xee))
    details.append("Waypoint (cm):  " + str(targ))
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 0.6
    thickness = 2
    dp_x = 5
    dp_y = 790
    dp_del = 20
    cv2.rectangle(img, (0,dp_y-20), (300,730), white, -1)
    for i, text in enumerate(details):
        details_p = (dp_x, dp_y + (dp_del * i)) 
        color_pick = black
        if "Xee" in text:
            color_pick = color
        elif "Waypoint" in text:
            color_pick = red
        cv2.putText(img, text, details_p, font, fontScale, color_pick, thickness)


def make_traj_video(out, direction):
    if direction[0] == "up":
        up = True
        down = False
    else:
        up = False
        down = True
    if direction[1] == "right":
        right = True
        left = False
    else:
        right = False
        left = True

    previous_trajectories = []
    for cid in range(len(controllers)):
        directory = traj_dir + controllers[cid] + "_arc_" + direction[0] + "_" + direction[1] + "_100/"
        csv_file = directory + "control_data_-9_25.csv"
        imgs_dir = directory + "imgs"
        df = pd.read_csv(csv_file)

        df = df.reset_index()
        df = df[df["WAYY"] != 24.0].reset_index()
        df = df.drop_duplicates(subset=['WAYX', 'WAYY'], keep='first')
        if len(df) != 100:
            print(len(df))
            print(df)
        # print(df)

        xee_prev = []
        # for idx, filename in enumerate(sorted(glob.glob(imgs_dir + '/*.jpg'), key=os.path.getmtime)):
        # quit()
        for idx in range(len(df)):
            filename = imgs_dir + "/img" + str(df.iloc[idx]["index"]) + ".jpg"
            # print(filename)
            # print(filename)
            img = cv2.imread(filename)
            oxw = df.iloc[idx]["ORIGX"]
            oyw = df.iloc[idx]["ORIGY"]
            origin = (oxw, oyw)
            xw = oxw + df.iloc[idx]["XEEX"]
            yw = oyw - df.iloc[idx]["XEEY"]
            tx = oxw + df.iloc[idx]["WAYX"]
            ty = oyw - df.iloc[idx]["WAYY"]
            tw = (tx, ty)
            
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

            xee = world2pix(xw, yw)
            orig = world2pix(oxw, oyw)
            targ = world2pix(tx, ty)

            for pt in range(len(previous_trajectories)):
                draw_path(img, previous_trajectories[pt], controller_colors[pt])

            xee_prev.append(xee)
            draw_path(img, xee_prev, controller_colors[cid])

            cv2.circle(img, targ, radius, red, 3)
            cv2.circle(img, xee, radius, controller_colors[cid], 3)

            # zoom and crop
            img = zoom_at(img, 1.75)

            # add white boxes
            cv2.rectangle(img, (0,0), (350, 1080), white, -1)
            cv2.rectangle(img, (1620,0), (1920, 1080), white, -1)

            add_pressure_box(img, df, idx)
            add_title_box(img, controller_names[cid], controller_colors[cid])

            waypoint = (round(df.iloc[idx]["WAYX"], 2), round(df.iloc[idx]["WAYY"], 2))
            distance = math.sqrt((df.iloc[idx]["WAYX"] - df.iloc[idx]["XEEX"])**2 + (df.iloc[idx]["WAYY"] - df.iloc[idx]["XEEY"])**2)
            controller_errors[cid].append(distance)
            distance = round(distance, 2)
            xee_round = (round(df.iloc[idx]["XEEX"], 2), round(df.iloc[idx]["XEEY"], 2))

            add_text(img, distance, xee_round, waypoint, controller_colors[cid])

            out.write(img)

        previous_trajectories.append(xee_prev)


def create_video(out):
    make_traj_video(out, ("down", "right"))
    make_traj_video(out, ("up", "right"))
    make_traj_video(out, ("down", "left"))
    make_traj_video(out, ("up", "left"))
    for er in controller_errors:
        print(sum(er) / len(er))


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

