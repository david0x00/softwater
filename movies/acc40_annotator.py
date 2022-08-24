import csv
import cv2
import numpy as np
import glob
import os
import pandas as pd

mtx = np.array([
    [1535.10668 / 1.5, 0, 954.393136 / 1.5],
    [0, 1530.80529 / 1.5, 543.030187 / 1.5],
    [0,0,1]
])

newcameramtx = np.array([
    [1559.8905 / 1.5, 0, 942.619458 / 1.5],
    [0, 1544.98389 / 1.5, 543.694259 / 1.5],
    [0,0,1]
])

inv_camera_mtx = np.linalg.inv(newcameramtx)

dist = np.array([[0.19210016, -0.4423498, 0.00093771, -0.00542759, 0.25832642 ]])

camera_to_markers_dist = 57.055 #cm

directory = "/Users/davidnull/Desktop/Acc40_Visual_Servo_r1/Visual_Servo IDX0 14-33-53 8-23-2022/"
imgs_dir = directory + "imgs/"
proj_dir = "/Users/davidnull/Desktop/acc40_visual_servo_analysis/"
proj_name = "vs0"

size = (1280,720)

def world2pix(x, y):
        coord_3d = np.array([
            x / camera_to_markers_dist,
            y / camera_to_markers_dist,
            1
        ])
        coord_2d = np.matmul(newcameramtx, coord_3d)
        return int(coord_2d[0]), int(coord_2d[1])

        # world_objects = []
        # for obj_id in objects.keys():
        #     coord_2d = np.array([[objects[obj_id].x],
        #                             [objects[obj_id].y],
        #                             [1]])
        #     coord_3d = np.matmul(inv_camera_mtx, coord_2d) * camera_to_markers_dist
        #     world_objects.append((coord_3d[0][0], coord_3d[1][0]))
        # return world_objects

if __name__ == "__main__":

    file_name = proj_dir + proj_name + ".mp4"
    hz = 2
    speed = 2
    fps = speed * hz
    mp4_codec = cv2.VideoWriter_fourcc(*'X264')
    avi_codec = cv2.VideoWriter_fourcc(*'DIVX')
    out = cv2.VideoWriter(file_name, mp4_codec, fps, size)

    csv_file = glob.glob(directory + '/*.csv')[0]
    df = pd.read_csv(csv_file)
    
    radius = 5
    red = (0, 0, 255)
    green = (0, 255, 0)
    blue = (255, 0, 0)
    white = (255, 255, 255)
    black = (0, 0, 0)

    xee_prev = []

    for idx, filename in enumerate(sorted(glob.glob(imgs_dir + '/*.jpg'), key=os.path.getmtime)):
        img = cv2.imread(filename)
        img = cv2.undistort(img, mtx, dist, None, newcameramtx)
        oxw = df.iloc[idx]["ORIGX"]
        oyw = df.iloc[idx]["ORIGY"]
        xw = oxw + df.iloc[idx]["XEEX"]
        yw = oyw - df.iloc[idx]["XEEY"]
        tx = oxw + df.iloc[idx]["TARGX"]
        ty = oyw - df.iloc[idx]["TARGY"]
        atx = oxw + df.iloc[idx]["ADJ_TARGX"]
        aty = oyw - df.iloc[idx]["ADJ_TARGY"]
        

        xee = world2pix(xw, yw)
        orig = world2pix(oxw, oyw)
        targ = world2pix(tx, ty)
        adjtarg = world2pix(atx, aty)
        cv2.circle(img, xee, radius, red, 3)
        cv2.circle(img, targ, radius, blue, 3)
        cv2.circle(img, adjtarg, radius, green, 3)
        cv2.drawMarker(img, orig, red, cv2.MARKER_CROSS, thickness=3)

        for prev in range(len(xee_prev)):
            cv2.line(img, xee_prev, xee, red, thickness=3)
        xee_prev.append(xee)

        for i in range(1,10):
            mx = oxw + df.iloc[idx]["M" + str(i) + "X"]
            my = oyw - df.iloc[idx]["M" + str(i) + "Y"]
            m = world2pix(mx, my)
            cv2.circle(img, m, radius, red, 3)

        # cv2.putText
        # cv2.rectangle()
        # cv2.line()

        out.write(img)
    
    out.release()