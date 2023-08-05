
import csv
import cv2
import numpy as np
import glob
import pandas as pd

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

camera_to_markers_dist = 77.47 #cm

red = (0, 0, 255)
radius = 5

def world2pix(x, y):
        coord_3d = np.array([
            x / camera_to_markers_dist,
            y / camera_to_markers_dist,
            1
        ])
        coord_2d = np.matmul(newcameramtx, coord_3d)
        return int(coord_2d[0]), int(coord_2d[1])





def annotate_img(data_dir, df, idx):
    img_file = data_dir + "/imgs/img" + str(idx) + ".jpg"
    img = cv2.imread(img_file)
    img = cv2.undistort(img, mtx, dist, None, newcameramtx)

    oxw = df.iloc[idx]["ORIGX"]
    oyw = df.iloc[idx]["ORIGY"]

    prev_left = None
    prev_right = None
    rl = 0
    ll = 0

    for i in range(1,7):
        mx = oxw + df.iloc[idx]["M" + str(i) + "X"]
        my = oyw - df.iloc[idx]["M" + str(i) + "Y"]
        m = world2pix(mx, my)
        mxl = oxw + df.iloc[idx]["M" + str(i) + "XL"]
        myl = oyw - df.iloc[idx]["M" + str(i) + "YL"]
        ml = world2pix(mxl, myl)
        mxr = oxw + df.iloc[idx]["M" + str(i) + "XR"]
        myr = oyw - df.iloc[idx]["M" + str(i) + "YR"]
        mr = world2pix(mxr, myr)
        cv2.circle(img, m, radius, red, 3)
        cv2.circle(img, ml, radius, red, 3)
        cv2.circle(img, mr, radius, red, 3)

        # if prev_left is not None:
        #     ll += np.sqrt((prev_left[0] - df.iloc[idx]["M" + str(i) + "XL"])**2 + (prev_left[1] - df.iloc[idx]["M" + str(i) + "YL"])**2)
        #     rl += np.sqrt((prev_right[0] - df.iloc[idx]["M" + str(i) + "XR"])**2 + (prev_right[1] - df.iloc[idx]["M" + str(i) + "YR"])**2)
        #     print(ll, rl)
        # prev_left = (df.iloc[idx]["M" + str(i) + "XL"], df.iloc[idx]["M" + str(i) + "YL"])
        # prev_right = (df.iloc[idx]["M" + str(i) + "XR"], df.iloc[idx]["M" + str(i) + "YR"])
    return img

def get_img(data_dir, idx):
    csv_file = training_data_dir + "/new_data.csv"
    df = pd.read_csv(csv_file)
    # print(df.iloc[idx]["M1-AL-L"])
    # print(df.iloc[idx]["M1-AR-L"])
    # print(df.iloc[idx]["A1"])
    # print(df.iloc[idx]["A2"])
    # print(df.iloc[idx][["M1X", "M2X", "M3X", "M4X", "M5X", "M6X"]])
    # print(df.iloc[idx][["M1Y", "M2Y", "M3Y", "M4Y", "M5Y", "M6Y"]])
    img = annotate_img(data_dir, df, idx)
    cv2.imshow('image',img)
    cv2.waitKey(0)
    return img

def make_movie(data_dir):
    proj_name = "movie_annotation"
    size = (1920,1080)
    file_name = data_dir + proj_name + ".mp4"
    hz = 2
    speed = 6
    fps = speed * hz
    mp4_codec = cv2.VideoWriter_fourcc(*'X264')
    out = cv2.VideoWriter(file_name, mp4_codec, fps, size)

    csv_file = training_data_dir + "/new_data.csv"
    df = pd.read_csv(csv_file)
    for index, row in df.iterrows():
        img = annotate_img(data_dir, df, index)
        out.write(img)

    out.release()


# idx = 382
idx = 375
training_data_dir = "/Users/davidnull/phd/data/3rd_stage_base_training/Manual IDX0 13-40-24 5-16-2023/"
# training_data_dir = "/Users/davidnull/phd/data/3rd_stage_base_training/Manual IDX0 13-53-33 5-16-2023/"
# training_data_dir = "/Users/davidnull/phd/data/3rd_stage_base_training/Manual IDX0 14-2-39 5-16-2023/"
# training_data_dir = "/Users/davidnull/phd/data/3rd_stage_base_training/Manual IDX0 14-14-7 5-16-2023/"
# training_data_dir = "/Users/davidnull/phd/data/3rd_stage_base_training/Manual IDX0 14-18-34 5-16-2023/"
# training_data_dir = "/Users/davidnull/phd/data/LRRL1518/Length 1LR 14-46-56 5-17-2023/"
# training_data_dir = "/Users/davidnull/phd/data/LRRL1518/Length 1RL 14-40-21 5-17-2023/"

img = get_img(training_data_dir, idx)
cv2.imwrite("annotated_img.jpg", img)
# make_movie(training_data_dir)