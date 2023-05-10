import cv2
import os
import glob
import numpy as np
import math
import pandas as pd
import pickle
import statistics
from matplotlib import cm
from matplotlib import pyplot as plt
from sklearn.metrics import mean_squared_error
import matplotlib.patches as patches
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, Normalize
from PIL import Image
import ast

# mtx = np.array([
#     [1535.10668, 0, 954.393136],
#     [0, 1530.80529, 543.030187],
#     [0,0,1]
# ])

# newcameramtx = np.array([
#     [1559.8905, 0, 942.619458],
#     [0, 1544.98389, 543.694259],
#     [0,0,1]
# ])
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

def world2pix(x, y):
        coord_3d = np.array([
            x / camera_to_markers_dist,
            y / camera_to_markers_dist,
            1
        ])
        coord_2d = np.matmul(newcameramtx, coord_3d)
        return int(coord_2d[0]), int(coord_2d[1])

df = pd.read_csv("./end_data.csv")
# fig, (ax1, ax2) = plt.subplots(1, 2)

# imgs = ['./left.jpg', './rightol.jpg']
imgs = ['./left_back.jpg', './mid_back.jpg', './right_back.jpg']
# targs = [(-9.0,27.0), (9.0,27.0)]
targs = [(-9.0,27.0), (1.0,33.0), (9.0, 27.0)]
radius = 5
red = (0, 0, 255)
purple = (219,112,147)
light_green = (144, 238, 144)
dark_green = (0, 150, 0)
green = (0, 255, 0)
orange = (0, 165, 255)
yellow = (0, 255, 255)
light_blue = (211, 156, 75)
blue = (150, 0, 0)
white = (255, 255, 255)
black = (0, 0, 0)
grey = (91, 96, 100)

for idx, imgname in enumerate(imgs):
    img = cv2.imread(imgname)
    img = cv2.undistort(img, mtx, dist, None, newcameramtx)

    # a_channel = np.ones(img.shape, dtype=np.float)/2.0
    # img = img*a_channel

    targ = targs[idx]
    targx = targ[0]
    targy = targ[1]

    data1 = df.loc[df['x'] == targ[0]]
    data = data1.loc[data1['y'] == targ[1]]


    # ox = data["origx_ampc"].iloc[0] + 1.3
    # oy = data["origy_ampc"].iloc[0] - 0.5
    ox = data["origx_ampc"].iloc[0]
    oy = data["origy_ampc"].iloc[0]

    tx = ox + targ[0]
    ty = oy - targ[1]

    targ = world2pix(tx, ty)
    print(data["ampc_pathy"])
    
    # Draw Target Zone 
    target_color = black
    side_length = 20
    targ_c1 = (targ[0] - side_length, targ[1] - side_length)
    targ_c2 = (targ[0] + side_length, targ[1] + side_length)
    cv2.rectangle(img,targ_c1,targ_c2,target_color,3)
    vl_c1 = (targ[0], targ[1] - side_length)
    vl_c2 = (targ[0], targ[1] + side_length)
    cv2.line(img,vl_c1,vl_c2,target_color,3)
    hl_c1 = (targ[0] - side_length, targ[1])
    hl_c2 = (targ[0] + side_length, targ[1])
    cv2.line(img,hl_c1,hl_c2,target_color,3)
    # cv2.drawMarker(img, targ, black, cv2.MARKER_CROSS, thickness=3)
    # cv2.circle(img, targ, 10, black, 3)

    simp_pathx = [float(x) for x in " ".join(data["simp_pathx"].iloc[0][1:-1].split("\n")).split()]
    simp_pathy = [float(x) for x in " ".join(data["simp_pathy"].iloc[0][1:-1].split("\n")).split()]
    simp_dist = [np.sqrt((simp_pathx[i]-targx)**2 + (simp_pathy[i]-targy)**2) for i in range(len(simp_pathx))]
    vs_pathx = [float(x) for x in " ".join(data["vs_pathx"].iloc[0][1:-1].split("\n")).split()]
    vs_pathy = [float(x) for x in " ".join(data["vs_pathy"].iloc[0][1:-1].split("\n")).split()]
    vs_dist = [np.sqrt((vs_pathx[i]-targx)**2 + (vs_pathy[i]-targy)**2) for i in range(len(vs_pathx))]
    trpo_pathx = [float(x) for x in " ".join(data["trpo_pathx"].iloc[0][1:-1].split("\n")).split()]
    trpo_pathy = [float(x) for x in " ".join(data["trpo_pathy"].iloc[0][1:-1].split("\n")).split()]
    trpo_dist = [np.sqrt((trpo_pathx[i]-targx)**2 + (trpo_pathy[i]-targy)**2) for i in range(len(trpo_pathx))]
    cql_pathx = [float(x) for x in " ".join(data["cql_pathx"].iloc[0][1:-1].split("\n")).split()]
    cql_pathy = [float(x) for x in " ".join(data["cql_pathy"].iloc[0][1:-1].split("\n")).split()]
    cql_dist = [np.sqrt((cql_pathx[i]-targx)**2 + (cql_pathy[i]-targy)**2) for i in range(len(cql_pathx))]
    ampc_pathx = [float(x) for x in " ".join(data["ampc_pathx"].iloc[0][1:-1].split("\n")).split()]
    ampc_pathy = [float(x) for x in " ".join(data["ampc_pathy"].iloc[0][1:-1].split("\n")).split()]
    ampc_dist = [np.sqrt((ampc_pathx[i]-targx)**2 + (ampc_pathy[i]-targy)**2) for i in range(len(ampc_pathx))]

    circle_thickness = -1
    circle_radius = 8

    ol_color = light_blue
    for j in range(len(simp_pathx)-1):
        p1x = ox + float(simp_pathx[j])
        p1y = oy - float(simp_pathy[j])
        p1 = world2pix(p1x, p1y)
        
        p2x = ox + float(simp_pathx[j+1])
        p2y = oy - float(simp_pathy[j+1])
        p2 = world2pix(p2x, p2y)
        cv2.line(img, p1, p2, ol_color, thickness=3)

        if j == 0:
            cv2.circle(img, p1, circle_radius, ol_color, circle_thickness)
    cv2.circle(img, p2, circle_radius, ol_color, circle_thickness)

    vs_color = blue
    for j in range(len(vs_pathx)-1):
        p1x = ox + float(vs_pathx[j])
        p1y = oy - float(vs_pathy[j])
        p1 = world2pix(p1x, p1y)
        
        p2x = ox + float(vs_pathx[j+1])
        p2y = oy - float(vs_pathy[j+1])
        p2 = world2pix(p2x, p2y)
        cv2.line(img, p1, p2, vs_color, thickness=3)

        if j == 0:
            cv2.circle(img, p1, circle_radius, vs_color, circle_thickness)
    cv2.circle(img, p2, circle_radius, vs_color, circle_thickness)

    cql_color = light_green
    for j in range(len(cql_pathx)-1):
        p1x = ox + float(cql_pathx[j])
        p1y = oy - float(cql_pathy[j])
        p1 = world2pix(p1x, p1y)
        
        p2x = ox + float(cql_pathx[j+1])
        p2y = oy - float(cql_pathy[j+1])
        p2 = world2pix(p2x, p2y)
        cv2.line(img, p1, p2, cql_color, thickness=3)

        if j == 0:
            cv2.circle(img, p1, circle_radius, cql_color, circle_thickness)
    cv2.circle(img, p2, circle_radius, cql_color, circle_thickness)

    trpo_color = dark_green
    for j in range(len(trpo_pathx)-1):
        p1x = ox + float(trpo_pathx[j])
        p1y = oy - float(trpo_pathy[j])
        p1 = world2pix(p1x, p1y)
        
        p2x = ox + float(trpo_pathx[j+1])
        p2y = oy - float(trpo_pathy[j+1])
        p2 = world2pix(p2x, p2y)
        cv2.line(img, p1, p2, trpo_color, thickness=3)

        if j == 0:
            cv2.circle(img, p1, circle_radius, trpo_color, circle_thickness)
    cv2.circle(img, p2, circle_radius, trpo_color, circle_thickness)
    
    for j in range(len(ampc_pathx)-1):
        p1x = ox + float(ampc_pathx[j])
        p1y = oy - float(ampc_pathy[j])
        p1 = world2pix(p1x, p1y)
        
        p2x = ox + float(ampc_pathx[j+1])
        p2y = oy - float(ampc_pathy[j+1])
        p2 = world2pix(p2x, p2y)
        cv2.line(img, p1, p2, red, thickness=3)
        if j == 0:
            cv2.circle(img, p1, circle_radius, red, circle_thickness)
    cv2.circle(img, p2, circle_radius, red, circle_thickness)

    # fig, axs = plt.subplots(2)
    # # fig.suptitle('Vertically stacked subplots')
    # axs[0].plot(simp_pathx, simp_pathy)
    # axs[0].plot(vs_pathx, vs_pathy)
    # axs[0].plot(trpo_pathx, trpo_pathy)
    # axs[0].plot(cql_pathx, cql_pathy)
    # axs[0].plot(ampc_pathx, ampc_pathy)
    # axs[0].set_aspect('equal')
    # axs[0].set_xlabel("x (cm)")
    # axs[0].set_ylabel("y (cm)")
    # axs[0].set_title("End-effector Trajectories")

    
    # axs[1].plot(simp_dist, label="Open Loop IK")
    # axs[1].plot(vs_dist, label="Visual Servo")
    # axs[1].plot(cql_dist, label="CQL")
    # axs[1].plot(trpo_dist, label="TRPO")
    # axs[1].plot(ampc_dist, label="AutoMPC")
    # axs[1].set_xlabel("Error (cm)")
    # axs[1].set_ylabel("Time step")
    # axs[1].set_title("End-effector Distance Error")
    # axs[1].legend()
    # # axs[1].set_aspect('equal')
    # # axs[1].set_aspect('equal', 'box')
    # axs[1].set_xlim((0,100))
    # axs[1].set_ylim((0,11))


    # if idx == 0:
    #     axs[0].set_xlim((-12,1))
    #     axs[0].set_ylim((23,36))
    # if idx == 1:
    #     axs[0].set_xlim((-6.5,6.5))
    #     axs[0].set_ylim((23,36))
    # if idx == 2:
    #     axs[0].set_xlim((-1,12))
    #     axs[0].set_ylim((23,36))

    # plt.show()
    
    if idx == 0:
        cv2.imwrite("./leftann.jpg", img)
        # fig.savefig("./leftfig.jpg")
    if idx == 1:
        cv2.imwrite("./midann.jpg", img)
        # fig.savefig("./midfig.jpg")
    if idx == 2:
        cv2.imwrite("./rightann.jpg", img)
        # fig.savefig("./rightfig.jpg")
    






