import cv2
import os
import glob
import numpy as np
import pandas as pd
import math
import pickle
import statistics
from matplotlib import cm
from matplotlib import pyplot as plt
from sklearn.metrics import mean_squared_error
import matplotlib.patches as patches
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, Normalize
from PIL import Image
plt.rcParams['figure.dpi'] = 200

# im = Image.open('/Users/davidnull/phd/data/acc40_data/0.jpg')
all_df = pd.read_csv('/Users/davidnull/phd/data/acc40_data/all_df_combined.csv')

x_data = all_df["M10X"]
y_data = all_df["M10Y"]

train_count = {}
for x in range(-21,21,2):
    for y in range(19, 41,2):
        train_count[(x,y)] = 0
half_side = 1
for i in range(len(x_data)):
    x = x_data.iloc[i]
    y = y_data.iloc[i]  
    for key in train_count.keys():
        xu = key[0] + half_side
        xl = key[0] - half_side
        yu = key[1] + half_side
        yl = key[1] - half_side
        if (x < xu and x > xl and y < yu and y > yl):
            train_count[key] += 1

levels = 256
viridis_train = cm.get_cmap('gray', levels)
max_count = 250
min_count = 0
abs_max_count = 850
scaler = abs_max_count/max_count
newcolors_train = viridis_train(np.linspace(0, scaler, levels))
cmap_train = ListedColormap(newcolors_train)
half_side = 1

newcameramtx = np.array([
    [1559.8905, 0, 942.619458],
    [0, 1544.98389, 543.694259],
    [0,0,1]
])
camera_to_markers_dist = 57.055

def world2pix(x, y):
    coord_3d = np.array([[float(x) / camera_to_markers_dist],
                         [float(y) / camera_to_markers_dist],
                         [1.0]])
    coord_2d = np.matmul(newcameramtx, coord_3d)
    return coord_2d[0][0], coord_2d[1][0]
    
def draw_rectangle(img, loc, count):
    if loc[1] <= 21:
        return img
    # if count == 0:
    #     return img
    xr = loc[0] + half_side
    xl = loc[0] - half_side
    yt = loc[1] + half_side
    yb = loc[1] - half_side
    
    coord_2d_p1 = world2pix(xl, yt)
    coord_2d_p2 = world2pix(xr, yb)
    
    p1 = (int(coord_2d_p1[0]), 1080-(int(coord_2d_p1[1])-489))
    p2 = (int(coord_2d_p2[0]), 1080-(int(coord_2d_p2[1])-489))
    norm_count = (count - min_count) / (max_count - min_count)
    colorv = viridis_train(norm_count)
    color = (colorv[0] * 256, colorv[1] * 256, colorv[2] * 256)
    return cv2.rectangle(img,p1,p2,color,cv2.FILLED)

def draw_line(img, loc, left=False, right=False, top=False, bottom=False, color=(255,0,0), side_length=half_side):
    xr = loc[0] + side_length
    xl = loc[0] - side_length
    yt = loc[1] + side_length
    yb = loc[1] - side_length
    
    if left:
        coord_2d_p1 = world2pix(xl, yt)
        coord_2d_p2 = world2pix(xl, yb)
    elif right:
        coord_2d_p1 = world2pix(xr, yt)
        coord_2d_p2 = world2pix(xr, yb)
    elif top:
        coord_2d_p1 = world2pix(xl, yt)
        coord_2d_p2 = world2pix(xr, yt)
    elif bottom:
        coord_2d_p1 = world2pix(xl, yb)
        coord_2d_p2 = world2pix(xr, yb)
    else:
        coord_2d_p1 = 0
        coord_2d_p2 = 0
    
    p1 = (int(coord_2d_p1[0]), 1080-(int(coord_2d_p1[1])-489))
    p2 = (int(coord_2d_p2[0]), 1080-(int(coord_2d_p2[1])-489))
    return cv2.line(img,p1,p2,color,5)


img = cv2.imread('/Users/davidnull/phd/data/acc40_data/0.jpg')
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
print(img.shape)
for key in train_count.keys():
    img = draw_rectangle(img, key, train_count[key])

lb = [(-9,25),(-9,27),(-7,29),(-5,31),(-3,33),(-1,35)]
rb = [(9,25),(9,27),(7,29),(5,31),(3,33),(1,35)]
tb = [(-9,27),(-7,29),(-5,31),(-3,33),(-1,35),(9,27),(7,29),(5,31),(3,33),(1,35)]
bb = [(-9,25),(-7,25),(-5,25),(-3,25),(-1,25),(1,25),(3,25),(5,25),(7,25),(9,25)]
for loc in lb:
    img = draw_line(img, loc, left=True)
for loc in rb:
    img = draw_line(img, loc, right=True)
for loc in tb:
    img = draw_line(img, loc, top=True)
for loc in bb:
    img = draw_line(img, loc, bottom=True)

# lb = [(-13,25), (-13,27), (-13,29), (-11,31), (-9,33), (-7,35), (-5,37), (13,25), (13,27), (13,29), (11,31), (9,33), (7,35), (5,37)]
# rb = [(-13,25), (-13,27), (-13,29), (-11,31), (-9,33), (-7,35), (-5,37), (13,25), (13,27), (13,29), (11,31), (9,33), (7,35), (5,37)]
# bb = [(-13,25), (-11,31), (-9,33), (-7,35), (-5,37), (13,25), (11,31), (9,33), (7,35), (5,37)]
# tb = [(-13,29), (-11,31), (-9,33), (-7,35), (-5,37), (13,29), (11,31), (9,33), (7,35), (5,37)]
# for loc in lb:
#     img = draw_line(img, loc, left=True, color=(0,255,0))
# for loc in rb:
#     img = draw_line(img, loc, right=True, color=(0,255,0))
# for loc in tb:
#     img = draw_line(img, loc, top=True, color=(0,255,0))
# for loc in bb:
#     img = draw_line(img, loc, bottom=True, color=(0,255,0))

lb = [(-9,25), (-5,27), (-3, 31), (-1,35), (-1,25), (9,25), (5,27), (3, 31), (1,35), (1,25)]
rb = [(-9,25), (-5,27), (-3, 31), (-1,35), (-1,25), (9,25), (5,27), (3, 31), (1,35), (1,25)]
bb = [(-9,25), (-5,27), (-3, 31), (-1,35), (-1,25), (9,25), (5,27), (3, 31), (1,35), (1,25)]
tb = [(-9,25), (-5,27), (-3, 31), (-1,35), (-1,25), (9,25), (5,27), (3, 31), (1,35), (1,25)]
for loc in lb:
    img = draw_line(img, loc, left=True, color=(0,0,255), side_length=0.75)
for loc in rb:
    img = draw_line(img, loc, right=True, color=(0,0,255), side_length=0.75)
for loc in tb:
    img = draw_line(img, loc, top=True, color=(0,0,255), side_length=0.75)
for loc in bb:
    img = draw_line(img, loc, bottom=True, color=(0,0,255), side_length=0.75)

# plt.imshow(img)
# plt.show()
# final_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
# cv2.imwrite('/Users/davidnull/phd/data/acc40_data/combined_data_visualv2.png', final_img)

# fig_new, ax_new = plt.subplots()
# norm = Normalize(vmin=0, vmax=abs_max_count, clip=False)
# cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap_train), ax=ax_new)
# cbar.set_label('# of Training Samples')
# plt.savefig('/Users/davidnull/phd/data/acc40_data/combined_data_visual_cbarv1.png')


plt.show()
final_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
cv2.imwrite('/Users/davidnull/phd/data/acc40_data/combined_data_visual_taskspace_tasks.png', final_img)