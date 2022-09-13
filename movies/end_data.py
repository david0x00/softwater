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

ol_dir = "/Users/davidnull/phd/data/acc40/"
vs_dir = "/Users/davidnull/phd/data/Acc40_Visual_Servo_r1/"
ampc_dir = "/Users/davidnull/phd/data/Acc40_Ampc_r1/"

def get_end_rmse(directory):
    for filename in glob.glob(directory + "*.csv"):
        if "debug_log" not in filename:
            data_arr = filename.split("/")[-1].split(".")[0].split("_")
            targ = (float(data_arr[-2]), float(data_arr[-1]))
            df = pd.read_csv(filename)
            end_targ = (float(df["M10X"].iloc[-1]), float(df["M10Y"].iloc[-1]))
            #rms = mean_squared_error(targ, end_targ, squared=False)
            rms = math.sqrt((targ[0] - end_targ[0])*(targ[0] - end_targ[0]) + (targ[1] - end_targ[1])*(targ[1] - end_targ[1]))
            # rms = df["RMSE"].iloc[-1]
            print("Goal: " + str(targ) + ", Actual: " + str(end_targ) + ", RMSE: " + str(rms) + " cm")
            
            m10x = df["M10X"].values
            m10y = df["M10Y"].values

            if ampc_dir in directory:
                origx = float(df["ORIGX"].iloc[-1])
                origy = float(df["ORIGY"].iloc[-1])
            else:
                origx = None
                origy = None
            
            return targ, end_targ, rms, m10x, m10y, origx, origy
            
data = {}
for targ_dir in glob.glob(ampc_dir + "/*"):
    details = get_end_rmse(targ_dir + "/")
    if details != None:
        targ_ampc, end_targ_ampc, rms_ampc, m10x_ampc, m10y_ampc, origx, origy = details
        data[targ_ampc] = {
            "targ": targ_ampc,
            "ampc_end": end_targ_ampc,
            "ampc_rms": rms_ampc,
            "ampc_pathx": m10x_ampc,
            "ampc_pathy": m10y_ampc,
            "origx_ampc": origx,
            "origy_ampc": origy
        }

for targ_dir in glob.glob(vs_dir + "/*"):
    details = get_end_rmse(targ_dir + "/")
    if details != None:
        targ_vs, end_targ_vs, rms_vs, m10x_vs, m10y_vs, _, _= details
        data[targ_vs]["vs_end"] = end_targ_vs
        data[targ_vs]["vs_rms"] = rms_vs
        data[targ_vs]["vs_pathx"] = m10x_vs
        data[targ_vs]["vs_pathy"] = m10y_vs

for targ_dir in glob.glob(ol_dir + "/*"):
    if targ_dir.split("/")[-1].isnumeric():
        simple_dir = targ_dir + "/simple_comb/run0/"
        targ_simp, end_targ_simp, rms_simp, m10x_simp, m10y_simp, _, _ = get_end_rmse(simple_dir)
        data[targ_simp]["simp_end"] = end_targ_simp
        data[targ_simp]["simp_rms"] = rms_simp
        data[targ_simp]["simp_pathx"] = m10x_simp
        data[targ_simp]["simp_pathy"] = m10y_simp

print(data)

df = pd.DataFrame(data).T.reset_index().rename(columns={"level_0": "x", "level_1": "y"})
df.to_csv("./end_data.csv")

