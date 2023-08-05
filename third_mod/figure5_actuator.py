from matplotlib import cm
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, Normalize
import pandas as pd
import numpy as np
import glob
import os


def get_theoretical_actuator_paths():
    paths = []

    left_start = 12
    right_start = 12

    left_end = 15
    right_end = 18

    for steps in [1,2,4,8]:
        for b in [True, False]:
            choose_left = b
            left_sequence = [left_start]
            right_sequence = [right_start]
            for i in range(steps):
                next_left = left_start + (((left_end - left_start) / steps) * (i + 1))
                next_right = right_start + (((right_end - right_start) / steps) * (i + 1))
                left_sequence.append(next_left)
                right_sequence.append(next_right)
            left = [left_sequence[0]]
            right = [right_sequence[0]]
            for i in range(1, len(left_sequence)):
                if choose_left:
                    left.append(left_sequence[i])
                    right.append(right_sequence[i-1])
                    left.append(left_sequence[i])
                    right.append(right_sequence[i])
                else:
                    left.append(left_sequence[i-1])
                    right.append(right_sequence[i])
                    left.append(left_sequence[i])
                    right.append(right_sequence[i])
                
            paths.append([left, right])

    return paths

def get_actual_actuator_paths():
    paths = [None] * 8

    all_data_dir = "/Users/davidnull/phd/data/LRRL1518"
    data_dirs = list(glob.glob(all_data_dir + "/*"))

    for data_dir in data_dirs:
        id = data_dir.split(" ")[1]
        idx_map = {"1":0, "2":1, "4":2, "8":3}
        idx = idx_map[id[0]] * 2
        if id[1] == "R":
            idx += 1

        csv_file = data_dir + "/new_data.csv"
        df = pd.read_csv(csv_file)
        df = df.where( (((df["M1-AL-L"] >= 12) & (df["M1-AR-L"] >= 12)) | ((df["M1-AL-L"] > 15.2) | (df["M1-AR-L"] > 18.2))))
        left = list(df["M1-AL-L"])
        right = list(df["M1-AR-L"])
        paths[idx] = [left, right]
    return paths
colors = ['red', 'orange', 'green', 'blue']

fig = plt.figure()
fig.set_size_inches(21, 7)
axs = []
axs.append(fig.add_subplot(141)) 
axs.append(fig.add_subplot(142)) 
axs.append(fig.add_subplot(143)) 
axs.append(fig.add_subplot(144))

th_paths = get_theoretical_actuator_paths()
ac_paths = get_actual_actuator_paths()

for i in range(4):
    i1 = i*2
    i2 = (i*2)+1
    path1 = th_paths[i1]
    path2 = th_paths[i2]
    apath1 = ac_paths[i1]
    apath2 = ac_paths[i2]
    axs[i].plot(path1[1], path1[0], color="black")                
    axs[i].plot(path2[1], path2[0], linestyle="dashed", color="black")                
    axs[i].plot(apath1[1], apath1[0], color=colors[i])
    axs[i].plot(apath2[1], apath2[0], linestyle="dashed", color=colors[i])                
    axs[i].set(adjustable='box', aspect='equal')
    axs[i].set_ylim((11.8,16.75))
    axs[i].set_xlim((11.8,19))
    axs[i].set_xlabel("Right Actuator Length")
    axs[i].set_ylabel("Left Actuator Length")

plt.show()
    
