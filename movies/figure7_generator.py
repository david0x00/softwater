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

imgs = ['./left.jpg', './right.jpg']
targs = [(-9.0,27.0), (9.0,27.0)]
radius = 5
red = (0, 0, 255)
green = (0, 255, 0)
orange = (0, 165, 255)
yellow = (0, 255, 255)
blue = (255, 0, 0)
white = (255, 255, 255)
black = (0, 0, 0)

for idx, imgname in enumerate(imgs):
    img = cv2.imread(imgname)
    img = cv2.undistort(img, mtx, dist, None, newcameramtx)
    targ = targs[idx]

    data1 = df.loc[df['x'] == targ[0]]
    data = data1.loc[data1['y'] == targ[1]]

    ox = data["origx_ampc"].iloc[0]
    oy = data["origy_ampc"].iloc[0]

    tx = ox + targ[0]
    ty = oy - targ[1]

    targ = world2pix(tx, ty)
    print(data["ampc_pathy"])

    simp_pathx = " ".join(data["simp_pathx"].iloc[0][1:-1].split("\n")).split()
    simp_pathy = " ".join(data["simp_pathy"].iloc[0][1:-1].split("\n")).split()
    for j in range(len(simp_pathx)-1):
        p1x = ox + float(simp_pathx[j])
        p1y = oy - float(simp_pathy[j])
        p1 = world2pix(p1x, p1y)
        
        p2x = ox + float(simp_pathx[j+1])
        p2y = oy - float(simp_pathy[j+1])
        p2 = world2pix(p2x, p2y)
        cv2.line(img, p1, p2, yellow, thickness=3)

        if j == 0:
            cv2.circle(img, p1, 5, yellow, 3)
    cv2.circle(img, p2, 5, yellow, 3)

    vs_pathx = " ".join(data["vs_pathx"].iloc[0][1:-1].split("\n")).split()
    vs_pathy = " ".join(data["vs_pathy"].iloc[0][1:-1].split("\n")).split()
    for j in range(len(vs_pathx)-1):
        p1x = ox + float(vs_pathx[j])
        p1y = oy - float(vs_pathy[j])
        p1 = world2pix(p1x, p1y)
        
        p2x = ox + float(vs_pathx[j+1])
        p2y = oy - float(vs_pathy[j+1])
        p2 = world2pix(p2x, p2y)
        cv2.line(img, p1, p2, green, thickness=3)

        if j == 0:
            cv2.circle(img, p1, 5, green, 3)
    cv2.circle(img, p2, 5, green, 3)
    

    

    ampc_pathx = " ".join(data["ampc_pathx"].iloc[0][1:-1].split("\n")).split()
    ampc_pathy = " ".join(data["ampc_pathy"].iloc[0][1:-1].split("\n")).split()
    for j in range(len(ampc_pathx)-1):
        p1x = ox + float(ampc_pathx[j])
        p1y = oy - float(ampc_pathy[j])
        p1 = world2pix(p1x, p1y)
        
        p2x = ox + float(ampc_pathx[j+1])
        p2y = oy - float(ampc_pathy[j+1])
        p2 = world2pix(p2x, p2y)
        cv2.line(img, p1, p2, red, thickness=3)
        if j == 0:
            cv2.circle(img, p1, 5, red, 3)
    cv2.circle(img, p2, 5, red, 3)
    
    cv2.drawMarker(img, targ, black, cv2.MARKER_CROSS, thickness=3)
    cv2.circle(img, targ, 10, black, 3)
    if idx == 0:
        cv2.imwrite("./leftann.jpg", img)
    if idx == 1:
        cv2.imwrite("./rightann.jpg", img)




