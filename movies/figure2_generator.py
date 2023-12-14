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

##### 720 image #######
# mtx = np.array([
#     [1535.10668 / 1.5, 0, 954.393136 / 1.5],
#     [0, 1530.80529 / 1.5, 543.030187 / 1.5],
#     [0,0,1]
# ])

# newcameramtx = np.array([
#     [1559.8905 / 1.5, 0, 942.619458 / 1.5],
#     [0, 1544.98389 / 1.5, 543.694259 / 1.5],
#     [0,0,1]
# ])

# inv_camera_mtx = np.linalg.inv(newcameramtx)

# dist = np.array([[0.19210016, -0.4423498, 0.00093771, -0.00542759, 0.25832642 ]])

# camera_to_markers_dist = 57.055 #cm
######################

######### 1080 image ################

newcameramtx = np.array([
    [1559.8905, 0, 942.619458],
    [0, 1544.98389, 543.694259],
    [0,0,1]
])
camera_to_markers_dist = 57.055

#####################################

im_height = 1080
# im_height = 720
# y_offset = 489
y_offset = 550
x_offset = 1

im = Image.open('/Users/davidnull/phd/data/acc40_data/0.jpg')
all_df = pd.read_csv('/Users/davidnull/phd/data/acc40_data/all_df_combined.csv')

x_data = all_df["M10X"]
y_data = all_df["M10Y"]

all_points = []
train_count = {}
for x in range(-21,21,2):
    for y in range(19, 41,2):
        train_count[(x,y)] = 0
half_side = 1
for i in range(len(x_data)):
    x = x_data.iloc[i]
    y = y_data.iloc[i]  
    all_points.append((x,y))
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


xc = [[-9,-7,-5,-3,-1,1,3,5,7,9],
      [-9,-7,-5,-3,-1,1,3,5,7,9],
      [-7,-5,-3,-1,1,3,5,7],
      [-5,-3,-1,1,3,5],
      [-3,-1,1,3],
      [-1,1]]
yc = 25
task_points = []
for i, row in enumerate(xc):
    for x in row:
        y = yc + i*2
        task_points.append([x,y])

ood_points = [[-13,25],[-13,27],[-13,29],[-11,31],[-9,33],[-7,35],[-5,37],[-3,39],[-1,39],[1,39],[3,39],[5,37],[7,35],[9,33],[11,31],[13,29],[13,27],[13,25]]

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
    
    p1 = (int(coord_2d_p1[0]), im_height-(int(coord_2d_p1[1])-y_offset))
    p2 = (int(coord_2d_p2[0]), im_height-(int(coord_2d_p2[1])-y_offset))
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
    
    p1 = (int(coord_2d_p1[0]), im_height-(int(coord_2d_p1[1])-y_offset))
    p2 = (int(coord_2d_p2[0]), im_height-(int(coord_2d_p2[1])-y_offset))
    return cv2.line(img,p1,p2,color,5)


def draw_point(img, loc, color=(0,0,0), radius=2):
    x, y = world2pix(loc[0], loc[1])
    loc_pix = (int(x), im_height - (int(y) - y_offset))
    return cv2.circle(img, loc_pix, radius=radius, color=color, thickness=-1)


# img = cv2.imread('/Users/davidnull/phd/data/acc40_data/0.jpg')
# img = cv2.imread('/Users/davidnull/phd/data/Acc40_Visual_Servo_OOD_r1/Visual_Servo IDX52 12-9-15 4-12-2023/imgs/img0.jpg')
img = np.ones((1080,1920,3), np.uint8) * 255
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
print(img.shape)
# for key in train_count.keys():
    # img = draw_rectangle(img, key, train_count[key])
for point in all_points:
    img = draw_point(img, point, radius=2)

for point in task_points:
    img = draw_point(img, point, color=(255,0,0), radius=8)

for point in ood_points:
    img = draw_point(img, point, color=(0,140,0), radius=8)

# lb = [(-9,25),(-9,27),(-7,29),(-5,31),(-3,33),(-1,35)]
# rb = [(9,25),(9,27),(7,29),(5,31),(3,33),(1,35)]
# tb = [(-9,27),(-7,29),(-5,31),(-3,33),(-1,35),(9,27),(7,29),(5,31),(3,33),(1,35)]
# bb = [(-9,25),(-7,25),(-5,25),(-3,25),(-1,25),(1,25),(3,25),(5,25),(7,25),(9,25)]
# for loc in lb:
#     img = draw_line(img, loc, left=True)
# for loc in rb:
#     img = draw_line(img, loc, right=True)
# for loc in tb:
#     img = draw_line(img, loc, top=True)
# for loc in bb:
#     img = draw_line(img, loc, bottom=True)

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
# cv2.imwrite('/Users/davidnull/phd/data/acc40_data/combined_data_visual_taskspace_tasks.png', final_img)
cv2.imwrite('/Users/davidnull/phd/papers/RA-L 2023/Revision/fig3_base.png', final_img)