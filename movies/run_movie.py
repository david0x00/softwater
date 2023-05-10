
import csv
import cv2
import numpy as np
import glob
import math
import pickle
import os
import pandas as pd
from detect import RobotDetector


# import autompc as ampc # Version: 0.2
# from autompc.sysid import MLP
# import ConfigSpace as CS
# import ast
# import sys

# sys.path.insert(0, "/Users/davidnull/phd/underwater_robot_autompc/utils") # Replace relative path to underwater_robot_autompc/utils
# import utils
# sys.path.insert(1, "/Users/davidnull/phd/underwater_robot_autompc/experiment_scripts") # Replace relative path to underwater_robot_autompc/experiment_scripts
# import generalization_experiment_01 as experiment

mint = [0, 0, 141]
#maxt = [141, 137, 255]
maxt = [133, 115, 255]
color_threshold = (np.array(mint), np.array(maxt))

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

detector = RobotDetector()

ampc_dir = "/Users/davidnull/phd/data/Acc40_Ampc_r1/"
vs_dir = "/Users/davidnull/phd/data/Acc40_Visual_Servo_r1/"
ol_dir = "/Users/davidnull/phd/data/acc40/"
proj_dir = "/Users/davidnull/phd/papers/Robosoft-23/oral_presentation/"
proj_name = "motion"
proj_ext = ".mp4"

size = (1280,720)
file_name = proj_dir + proj_name + proj_ext
hz = 2
speed = 4
fps = speed * hz
targ_list = [10]
radius = 5
red = (0, 0, 255)
green = (0, 255, 0)
orange = (0, 165, 255)
yellow = (0, 255, 255)
blue = (255, 0, 0)
white = (255, 255, 255)
black = (0, 0, 0)

dfed = pd.read_csv("./end_data.csv")

def world2pix(x, y):
        coord_3d = np.array([
            x / camera_to_markers_dist,
            y / camera_to_markers_dist,
            1
        ])
        coord_2d = np.matmul(newcameramtx, coord_3d)
        return int(coord_2d[0]), int(coord_2d[1])

def get_key(fp):
    filename = os.path.splitext(os.path.basename(fp))[0]
    int_part = filename.split()[0]
    return int(int_part)


def get_run_dirs(home_dir, run_idx):
    run_dirs = glob.glob(home_dir + "/*")
    for rd in run_dirs:
        if (" IDX" + str(run_idx) + " ") in rd:
            run_dir = rd + "/"
            break
    for fname in glob.glob(run_dir + '/*.csv'):
        if "debug_log" not in fname:
            csv_file = fname
            break
    imgs_dir = run_dir + "imgs/"
    return run_dir, csv_file, imgs_dir


def handle_ampc_run(run_idx, out):
    run_dir, csv_file, imgs_dir = get_run_dirs(ampc_dir, run_idx)


    for idx, filename in enumerate(sorted(glob.glob(imgs_dir + '/*.jpg'), key=os.path.getmtime)):
        print(filename)
        img = cv2.imread(filename)
        img = cv2.undistort(img, mtx, dist, None, newcameramtx)
        out.write(img)

    ampc_path = []
    return ampc_path

def create_video(targ, out):
    ampc_path = handle_ampc_run(targ, out)

if __name__ == "__main__":
    mp4_codec = cv2.VideoWriter_fourcc(*'X264')
    avi_codec = cv2.VideoWriter_fourcc(*'DIVX')
    out = cv2.VideoWriter(file_name, mp4_codec, fps, size)

    for targ in targ_list:
        create_video(targ, out)

    out.release()