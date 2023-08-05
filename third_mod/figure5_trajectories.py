from matplotlib import cm
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, Normalize
import pandas as pd
import numpy as np
import glob
import os


def get_actual_trajectories():
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
        x = list(df["M6X"])
        y = list(df["M6Y"])
        th = list(df["A2"])
        paths[idx] = [x, y, th]
    return paths

trajs = get_actual_trajectories()
t1 = trajs[6]
t2 = trajs[7]

ax = plt.axes(projection='3d')
colors = ['red', 'orange', 'green', 'blue']
ax.set_xlabel("x (cm)")
ax.set_ylabel("y (cm)")
ax.set_zlabel(r"$\phi$ (degrees)")
# Data for a three-dimensional line
for i in range(4):
    tl = trajs[(i*2)]
    tr = trajs[(i*2)+1]
    ax.plot3D(tl[0], tl[1], tl[2], colors[i])
    ax.plot3D(tr[0], tr[1], tr[2], colors[i], linestyle="dashed")

# for idx, t in enumerate(trajs):
#     ax.plot3D(t[0], t[1], t[2], colors[idx])
# ax.plot3D(t2[0], t2[1], t2[2], 'red')
plt.show()

fig = plt.figure()
fig.set_size_inches(21, 7)
axs = []
axs.append(fig.add_subplot(131))
axs.append(fig.add_subplot(132))
axs.append(fig.add_subplot(133))


for i in range(4):
    tl = trajs[(i*2)]
    tr = trajs[(i*2)+1]
    axs[0].plot(tl[0], tl[1], colors[i])
    axs[0].plot(tr[0], tr[1], colors[i], linestyle="dashed")
    axs[0].set_xlabel("x (cm)")
    axs[0].set_ylabel("y (cm)")
for i in range(4):
    tl = trajs[(i*2)]
    tr = trajs[(i*2)+1]
    axs[1].plot(tl[0], tl[2], colors[i])
    axs[1].plot(tr[0], tr[2], colors[i], linestyle="dashed")
    axs[1].set_xlabel("x (cm)")
    axs[1].set_ylabel(r"$\phi$ (degrees)")
for i in range(4):
    tl = trajs[(i*2)]
    tr = trajs[(i*2)+1]
    axs[2].plot(tl[1], tl[2], colors[i])
    axs[2].plot(tr[1], tr[2], colors[i], linestyle="dashed")
    axs[2].set_xlabel("y (cm)")
    axs[2].set_ylabel(r"$\phi$ (degrees)")
plt.show()