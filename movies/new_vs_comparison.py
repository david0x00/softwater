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

vs_dir = "/Users/davidnull/phd/data/Acc40_Visual_Servo_r1/"
new_dir = "/Users/davidnull/phd/data/Acc40_Visual_Servo_r2/"

def in_goal(curr, targ):
    x = curr[0]
    y = curr[1]
    xt = targ[0]
    yt = targ[1]

    if (x >= xt - 1.0) and (x <= xt + 1.0) and (y >= yt - 1.0) and (y <= yt + 1.0):
        return True
    else:
        return False

def get_details(directory, ood=False):
    for filename in glob.glob(directory + "*.csv"):
        if "debug_log" not in filename:
            data_arr = filename.split("/")[-1].split(".")[0].split("_")
            targ = (float(data_arr[-2]), float(data_arr[-1]))
            df = pd.read_csv(filename)
            end_targ = (float(df["M10X"].iloc[-1]), float(df["M10Y"].iloc[-1]))
            #rms = mean_squared_error(targ, end_targ, squared=False)
            dist = math.sqrt((targ[0] - end_targ[0])*(targ[0] - end_targ[0]) + (targ[1] - end_targ[1])*(targ[1] - end_targ[1]))
            # rms = df["RMSE"].iloc[-1]
            # print("Goal: " + str(targ) + ", Actual: " + str(end_targ) + ", Dist: " + str(dist) + " cm")
            
            m10x = df["M10X"].values
            m10y = df["M10Y"].values

            if vs_dir in directory:
                origx = float(df["ORIGX"].iloc[-1])
                origy = float(df["ORIGY"].iloc[-1])
            else:
                origx = None
                origy = None

            start_time = df["TIME"].iloc[0]
            prev_time = start_time
            
            reached = False
            reached_end = in_goal(end_targ, targ)
            time_first_reached = 0.0
            time_inside_goal = 0.0
            estopped = False

            if ood:
                time_outside_goal = 70.0
            else:
                time_outside_goal = 50.0

            for index, row in df.iterrows():
                curr_time = row["TIME"]
                elapsed_time = curr_time - start_time
                if elapsed_time > time_outside_goal:
                    break

                pressures = [row["M1-PL"], row["M1-PR"], row["M2-PL"], row["M2-PR"]]
                for p in pressures:
                    if p > 118.0:
                        estopped = True

                pos = (row["M10X"], row["M10Y"])
                if in_goal(pos, targ):
                    if (reached == False):
                        time_first_reached = curr_time - start_time
                        reached = True
                    time_inside_goal += curr_time - prev_time
                prev_time = curr_time
            
            time_outside_goal = time_outside_goal - time_inside_goal
            if time_outside_goal < 0:
                time_outside_goal = 0
            
            if estopped:
                reached_end = False
            
            return targ, end_targ, dist, m10x, m10y, origx, origy, reached, reached_end, time_first_reached, time_inside_goal, time_outside_goal, estopped

names = ["IDX0 ",
         "IDX1 ",
         "IDX2 ",
         "IDX3 ",
         "IDX4 ",
         "IDX5 ",
         "IDX6 ",
         "IDX7 ",
         "IDX8 ",
         "IDX9 ",
         "IDX10 ",
         "IDX11 ",
         "IDX12 ",
         "IDX18 ",
         "IDX22 "]


vs_end_data = {}
for targ_dir in glob.glob(vs_dir + "/*"):
    cont = False
    name = ""
    for n in names:
        if n in targ_dir:
            cont = True
            name = n
    if cont is True:
        details = get_details(targ_dir + "/")
        if details != None:
            targ, end_targ, dist, m10x, m10y, origx, origy, reached, reached_end, time_first_reached, time_inside_goal, time_outside_goal, estopped = details
            vs_end_data[name] = dist


new_end_data = {}
for targ_dir in glob.glob(new_dir + "/*"):
    cont = False
    name = ""
    for n in names:
        if n in targ_dir:
            cont = True
            name = n
    if cont is True:
        details = get_details(targ_dir + "/")
        if details != None:
            targ, end_targ, dist, m10x, m10y, origx, origy, reached, reached_end, time_first_reached, time_inside_goal, time_outside_goal, estopped = details
            new_end_data[name] = dist

print(vs_end_data)
# print(sum(vs_end_data) / len(vs_end_data))

print(new_end_data)
# print(sum(new_end_data)/ len(new_end_data))

for i in names:
    if new_end_data[i] < vs_end_data[i]:
        print(i)
        print(new_end_data[i])
        print(vs_end_data[i])