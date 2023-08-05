from matplotlib import cm
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, Normalize
from matplotlib.collections import LineCollection
from matplotlib.colors import BoundaryNorm
import pandas as pd
import numpy as np
import glob
import os
from mpl_toolkits.axes_grid1 import make_axes_locatable

# 18
# 58

N = 473

def get_data():
    start_idx = 213
    end_idx = 686
    data_dir = "/Users/davidnull/phd/data/3rd_stage_base_training/Manual IDX0 14-18-34 5-16-2023/"
    csv_file = data_dir + "/new_data.csv"
    df = pd.read_csv(csv_file)
    df = df.iloc[start_idx:end_idx, :]
    x = list(df["M6X"])
    y = list(df["M6Y"])
    th = list(df["A2"])
    traj = [x,y,th]

    pl = list(df["M1-PL"])
    pr = list(df["M1-PR"])
    press = [pl, pr]

    ll = list(df["M1-AL-L"])
    lr = list(df["M1-AR-L"])
    length = [ll, lr]

    sli = list(df["M1-AL-IN"])
    slo = list(df["M1-AL-OUT"])
    sri = list(df["M1-AR-IN"])
    sro = list(df["M1-AR-OUT"])
    sol = [sli,slo,sri,sro]
    return traj, press, length, sol

traj, press, length, sol = get_data()

# points = np.array(traj).T.reshape(-1, 1, 3)
# segments = np.concatenate([points[:-1], points[1:]], axis=1)

# lc = LineCollection(segments, cmap='viridis')
# # Set the values used for colormapping
# # lc.set_array(dydx)
# lc.set_linewidth(2)
# line = axs[0].add_collection(lc)
# # fig.colorbar(line, ax=axs[0])

ax = plt.axes(projection='3d')
viridis = cm.get_cmap('viridis', 256)

for i in range(len(traj[0])):
    ax.plot3D(traj[0][i:i+2], traj[1][i:i+2], traj[2][i:i+2], color=viridis(i/(N)))

# ax.plot3D(traj[0], traj[1], traj[2], 'red')
ax.set_xlabel("x (cm)")
ax.set_ylabel("y (cm)")
ax.set_zlabel(r"$\phi$ (degrees)")

plt.show()

fig = plt.figure()
fig.set_size_inches(21, 7)
axs = []
axs.append(fig.add_subplot(131))
axs.append(fig.add_subplot(132))
axs.append(fig.add_subplot(133))

# for i in range(3):
#     axs[i].set(adjustable='box', aspect='equal')

for i in range(len(traj[0])):
    axs[0].plot(traj[0][i:i+2], traj[1][i:i+2], color=viridis(i/(N)))
    axs[0].set_xlabel("x (cm)")
    axs[0].set_ylabel("y (cm)")
for i in range(len(traj[0])):
    axs[1].plot(traj[0][i:i+2], traj[2][i:i+2], color=viridis(i/(N)))
    axs[1].set_xlabel("x (cm)")
    axs[1].set_ylabel(r"$\phi$ (degrees)")
for i in range(len(traj[0])):
    cb = axs[2].plot(traj[1][i:i+2], traj[2][i:i+2], color=viridis(i/(N)))
    axs[2].set_xlabel("y (cm)")
    axs[2].set_ylabel(r"$\phi$ (degrees)")

norm = Normalize(vmin=0, vmax=236, clip=False)
divider = make_axes_locatable(axs[2])
cax = divider.append_axes("right", size="5%", pad=0.05)
cbar = plt.colorbar(cm.ScalarMappable(cmap=viridis), cax=cax)
cbar.set_label('Time (sec)')
cbar.mappable.set_clim(vmin=0,vmax=236)

plt.show()

fig = plt.figure()
fig.set_size_inches(21, 7)
axs = []
axs.append(fig.add_subplot(121))
axs.append(fig.add_subplot(122))

for i in range(len(traj[0])):
    axs[0].plot(press[1][i:i+2], press[0][i:i+2], color=viridis(i/(N)))
    axs[0].set_xlabel("Right Actuator Pressure (kPa)")
    axs[0].set_ylabel("Left Actuator Pressure (kPa)")
for i in range(len(traj[0])):
    axs[1].plot(length[1][i:i+2], length[0][i:i+2], color=viridis(i/(N)))
    axs[1].set_xlabel("Right Actuator Length (cm)")
    axs[1].set_ylabel("Left Actuator Length (cm)")

plt.show()