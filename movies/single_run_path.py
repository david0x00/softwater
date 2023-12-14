import pandas as pd
import numpy as np
import glob
import os
import cv2

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

camera_to_markers_dist = 57.055  #cm
# 1,11,20 - 8,18,27
# trpo_dir = "/Users/davidnull/phd/data/Acc40_TRPO_OOD_r1/"
trpo_dir = "/Users/davidnull/phd/data/Acc40_TRPO_r1/"
idx_id = " IDX" + str(27) + " "
run_list = [x[0] for x in os.walk(trpo_dir)]
for run in run_list:
    if idx_id in run:
        run_dir_ood = run
        break

# run_dir_ood = "/Users/davidnull/phd/data/Acc40_TRPO_OOD_r1/TRPO IDX44 21-59-44 4-11-2023/"
# run_dir_ood = "/Users/davidnull/phd/data/Acc40_TRPO_OOD_r1/TRPO IDX45 22-1-15 4-11-2023/"
run_dir_task = "/Users/davidnull/phd/data/Acc40_TRPO_r1/TRPO IDX0 15-17-21 3-17-2023/"

for fname in glob.glob(run_dir_ood + '/*.csv'):
    ood_csv_file = fname
# ood_csv_file = run_dir_ood + "/control_data_-9_33.csv"
# ood_csv_file = run_dir_ood + "/control_data_-7_35.csv"
img_dir = run_dir_ood + "/imgs/"
img_list = sorted(glob.glob(img_dir + '/*.jpg'), key=os.path.getmtime)
ood_final_img = img_list[-1]

task_csv_file = run_dir_task + "/control_data_-9_25.csv"
task_final_img = run_dir_task + "/imgs/img99.jpg"

csv_file = ood_csv_file
final_img = ood_final_img

targx = int(csv_file.split("/")[-1].split(".")[0].split("_")[-2])
targy = int(csv_file.split("/")[-1].split(".")[0].split("_")[-1])
# targy = 25
# targy = 35

radius = 5
red = (0, 0, 255)
green = (0, 255, 0)

df = pd.read_csv(csv_file)
img = cv2.imread(final_img)
img = cv2.undistort(img, mtx, dist, None, newcameramtx)

def draw_target_ampc(img, tw=None, targ=None, orig=None, color=red):
    cv2.circle(img, orig, radius, red, 3)
    tx = tw[0]
    ty = tw[1]
    tbox_side = 2
    tbox1x = tx - (tbox_side/2)
    tbox1y = ty - (tbox_side/2)
    tbox2x = tx + (tbox_side/2)
    tbox2y = ty + (tbox_side/2)
    tbox1 = world2pix(tbox1x, tbox1y)
    tbox2 = world2pix(tbox2x, tbox2y)
    cv2.circle(img, targ, radius, red, 3)
    cv2.rectangle(img, tbox1, tbox2, red, 3)
    return img

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

trpo_path = [[],[]]
for idx in range(len(df)):
    oxw = df.iloc[idx]["ORIGX"]
    oyw = df.iloc[idx]["ORIGY"]
    origin = (oxw, oyw)
    # for i in range(1,10):
    #     mx = oxw + df.iloc[idx]["M" + str(i) + "X"]
    #     my = oyw - df.iloc[idx]["M" + str(i) + "Y"]
    #     m = world2pix(mx, my)
    #     cv2.circle(img, m, radius, red, 3)
    xw = oxw + df.iloc[idx]["M10X"]
    yw = oyw - df.iloc[idx]["M10Y"]
    tx = oxw + targx
    ty = oyw - targy
    tw = (tx,ty)

    trpo_path[0].append(df.iloc[idx]["M10X"])
    trpo_path[1].append(df.iloc[idx]["M10Y"])

    xee = world2pix(xw, yw)
    orig = world2pix(oxw, oyw)
    targ = world2pix(tx, ty)
    img = draw_target_ampc(img, tw=tw, targ=targ, orig=orig)

# draw_prev_path(img, trpo_path, orig, green)

for j in range(len(trpo_path[0])):
    p1 = world2pix(oxw + trpo_path[0][j], oyw - trpo_path[1][j])
    if j == 0:
        cv2.circle(img, p1, radius, green, 3)

    if j < len(trpo_path[0])-1:
        p2 = world2pix(oxw + trpo_path[0][j+1], oyw - trpo_path[1][j+1])
        cv2.line(img, p1, p2, green, thickness=3)
    else:
        cv2.circle(img, p1, radius, green, 3)

cv2.imwrite("task_space_trpo_ex.jpg", img)
