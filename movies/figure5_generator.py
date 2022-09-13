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
from mpl_toolkits.axes_grid1 import make_axes_locatable

df = pd.read_csv("./end_data.csv")

fig = plt.figure()
fig.set_size_inches(21, 7)
ax1 = fig.add_subplot(131)
ax2 = fig.add_subplot(132)
ax3 = fig.add_subplot(133)
# ax4 = fig.add_subplot(144)




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
    rect = patches.Rectangle((x, y), edge_len, edge_len, color=color, ec=None)
    return rect

ax1.set(adjustable='box', aspect='equal')
ax2.set(adjustable='box', aspect='equal')
ax3.set(adjustable='box', aspect='equal')

for idx, row in df.iterrows():
    targ = ast.literal_eval(row["targ"])
    rms = row["simp_rms"]
    rect_simp = get_rectangle(targ, rms)
    ax1.add_patch(rect_simp)
for idx, row in df.iterrows():
    targ = ast.literal_eval(row["targ"])
    rms = row["vs_rms"]
    rect_vs = get_rectangle(targ, rms)
    ax2.add_patch(rect_vs)
for idx, row in df.iterrows():
    targ = ast.literal_eval(row["targ"])
    rms = row["ampc_rms"]
    rect_ampc = get_rectangle(targ, rms)
    ax3.add_patch(rect_ampc)
    
ax1.set_ylim((19,41))
ax1.set_xlim((-11,11))
ax2.set_ylim((19,41))
ax2.set_xlim((-11,11))
ax3.set_ylim((19,41))
ax3.set_xlim((-11,11))

ax1.set_xlabel("X (cm)", size=15)
ax2.set_xlabel("X (cm)", size=15)
ax3.set_xlabel("X (cm)", size=15)
ax1.set_ylabel("Y (cm)", size=15)
ax1.label_outer()
ax2.label_outer()
ax3.label_outer()



# comment out to remove color bar
norm = Normalize(vmin=0, vmax=abs_max_rms, clip=False)
divider = make_axes_locatable(ax3)
cax = divider.append_axes("right", size="5%", pad=0.05)
cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax)
cbar.set_label('RMSE (cm)')

# if e == 0:
#     plt.savefig(directory + "/analysis/" + "/simp_acc40.png")
# elif e == 1:
#     plt.savefig(directory + "/analysis/" + "/ampc_acc40.png")
# elif e == 2:
#     plt.savefig(directory + "/analysis/" + "/vs_acc40.png")

plt.subplots_adjust(wspace=0, hspace=0)
plt.show()