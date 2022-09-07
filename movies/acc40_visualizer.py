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

# directory = "/Users/davidnull/phd/data/new_controller_noresample"
# directory = "/Users/davidnull/phd/data/Acc40_Ampc_r1/"
directory = "/Users/davidnull/phd/data/Acc40_Visual_Servo_r1"

def get_end_rmse(directory):
    for filename in glob.glob(directory + "*.csv"):
        if "debug_log" not in filename:
            data_arr = filename.split("/")[-1].split(".")[0].split("_")
            targ = (float(data_arr[-2]), float(data_arr[-1]))
            df = pd.read_csv(filename)
            end_targ = (float(df["M10X"].iloc[-1]), float(df["M10Y"].iloc[-1]))
            #rms = mean_squared_error(targ, end_targ, squared=False)
            rms = math.sqrt((targ[0] - end_targ[0])*(targ[0] - end_targ[0]) + (targ[1] - end_targ[1])*(targ[1] - end_targ[1]))
            #rms = df["RMSE"].iloc[-1]
            print("Goal: " + str(targ) + ", Actual: " + str(end_targ) + ", RMSE: " + str(rms) + " cm")
            return targ, end_targ, rms

data = {}
for targ_dir in glob.glob(directory + "/*"):
    details = get_end_rmse(targ_dir + "/")
    if details != None:
        targ_ampc, end_targ_ampc, rms_ampc = details
        data[targ_ampc] = {
            "targ": targ_ampc,
            "ampc_end": end_targ_ampc,
            "ampc_rms": rms_ampc,
        }

levels = 256
viridis = cm.get_cmap('viridis', levels)
abs_max_rms = 4.635
max_rms = 3.5
min_rms = 0.0
scaler = abs_max_rms/max_rms
newcolors = viridis(np.linspace(0, scaler, levels))
cmap = ListedColormap(newcolors)

def get_rectangle(targ, rms):
    edge_len = 2
    half_edge = edge_len / 2
    x = targ[0] - half_edge
    y = targ[1] - half_edge
    norm_rms = (rms - min_rms) / (max_rms - min_rms)
    color = viridis(norm_rms)
    rect = patches.Rectangle((x, y), edge_len, edge_len, color=color)
    return rect

fig, ax = plt.subplots()

#0 - simp, 1 = ampc, vs = 2
e = 1
if e == 0:
    ax.set_title(r"$\bf{Open}$ $\bf{Loop}$ $\bf{Learned}$ $\bf{Inverse}$ $\bf{Kinematics}$ Accuracy")
    ax.set(adjustable='box', aspect='equal')
    simp_data_label = "simp_rms"
elif e == 1:
    ax.set_title(r"$\bf{AutoMPC}$ Accuracy")
    ampc_data_label = "ampc_rms"
    ax.set(adjustable="box", aspect='equal')
elif e == 2:
    ax.set_title(r"$\bf{Visual Servo}$ Accuracy")
    vs_data_label = "vs_rms"
    ax.set(adjustable="box", aspect='equal')


average = 0
stdev_list = []
for key in data.keys():
    if e == 0:
        rect_simp = get_rectangle(key, data[key][simp_data_label])
        ax.add_patch(rect_simp)
        average += data[key][simp_data_label]
        stdev_list.append(data[key][simp_data_label])
        
    elif e == 1:
        rect_ampc = get_rectangle(key, data[key][ampc_data_label])
        ax.add_patch(rect_ampc)
        average += data[key][ampc_data_label]
        stdev_list.append(data[key][ampc_data_label])
    elif e == 2:
        rect_vs = get_rectangle(key, data[key][vs_data_label])
        ax.add_patch(rect_vs)
        average += data[key][vs_data_label]
        stdev_list.append(data[key][vs_data_label])
average = average / len(data)
print(average)
stdev = statistics.pstdev(stdev_list)
print(stdev)
    

ax.set_ylim((19,41))
ax.set_xlim((-11,11))
ax.set_xlabel("X (cm)")
ax.set_ylabel("Y (cm)")
norm = Normalize(vmin=0, vmax=abs_max_rms, clip=False)
cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)
cbar.set_label('Root MSE (cm)')

if e == 0:
    plt.savefig(directory + "/analysis/" + "/simp_acc40.png")
elif e == 1:
    plt.savefig(directory + "/analysis/" + "/ampc_acc40.png")
elif e == 2:
    plt.savefig(directory + "/analysis/" + "/vs_acc40.png")


plt.show()