from turtle import done
import pandas as pd
import numpy as np
import cv2
import keras
import os
from tqdm import tqdm

fkmodel_path = "./fkmodel"
ikmodel_path = "./ikmodel"

experiments_dir = "./experiments"
video_dir = "./modelvideos"

lookback = 3

hz = 2
speed = 4

codec = cv2.VideoWriter_fourcc(*"mp4v")

#
#
#

fkmodel = keras.models.load_model(fkmodel_path)
ikmodel = keras.models.load_model(ikmodel_path)

norm_bounds = pd.read_csv("data/norm_bounds_basic.csv")

fk_x = ["M1-PL", "M1-PR", "M2-PL", "M2-PR",
        "M1-AL-IN", "M1-AR-IN", "M2-AL-IN", "M2-AR-IN",
        "M1-AL-OUT", "M1-AR-OUT", "M2-AL-OUT", "M2-AR-OUT"]

x_labels = len(fk_x)

new_fk_x = []
for i in range(lookback):
    for l in fk_x:
        new_fk_x.append(l + str(i))
fk_x += new_fk_x

fk_y = ["M1X", "M1Y", "M2X", "M2Y", "M3X", "M3Y",
            "M4X", "M4Y", "M5X", "M5Y", "M6X", "M6Y",
            "M7X", "M7Y", "M8X", "M8Y", "M9X", "M9Y",
            "M10X", "M10Y"]

y_lbl = ["ORIGX", "ORIGY"] + fk_y

ik_x = ["M1X", "M1Y", "M2X", "M2Y", "M3X", "M3Y",
        "M4X", "M4Y", "M5X", "M5Y", "M6X", "M6Y",
        "M7X", "M7Y", "M8X", "M8Y", "M9X", "M9Y",
        "M10X", "M10Y"]

ik_y = ["M1-PL", "M1-PR", "M2-PL", "M2-PR"]

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

dist = np.array([[0.19210016, -0.4423498, 0.00093771, -0.00542759, 0.25832642 ]])

camera_to_markers_dist = 57.055

def world2pix(pt):
    coord_3d = np.array([
        pt[0] / camera_to_markers_dist,
        pt[1] / camera_to_markers_dist,
        1
    ])
    coord_2d = np.matmul(newcameramtx, coord_3d)
    return int(coord_2d[0]), int(coord_2d[1])

def downscale(number, min, max):
    return (number - min) / (max - min)

def upscale(number, min, max):
    return (number * (max - min)) + min

def scale_data(fn, data, labels):
    ndata = []
    for idx, label in enumerate(labels):
        d = data[idx]
        min_val = norm_bounds.loc[0, label]
        max_val = norm_bounds.loc[1, label]
        ndata.append(fn(d, min_val, max_val))
    return np.array(ndata)

def draw_circle_line(img, pts, color, radius=7, circle_thickness=3, line_thickness=2):
    for i in range(pts.shape[0]):
        cv2.circle(img, pts[i], radius, color, circle_thickness)
    
    for i in range(pts.shape[0] - 1):
        cv2.line(img, pts[i], pts[i + 1], color, line_thickness)
    
red = (0, 0, 255)
green = (0, 255, 0)
blue = (255, 0, 0)
white = (255, 255, 255)
black = (0, 0, 0)

def draw_pressures(img, pressures, targ_pressures):
    ptop = 220
    pbot = 720
    pleft = 990
    pright = 1280
    pwidth = pright - pleft
    plength = pbot - ptop
    xpad = 60
    ypad = 20
    
    pbox_full_p1 = (pleft, ptop)
    pbox_full_p2 = (pright, pbot)
    cv2.rectangle(img, pbox_full_p1, pbox_full_p2, white, -1)
    cv2.rectangle(img, pbox_full_p1, pbox_full_p2, black, 1)
    ptitle_p1 = (pleft, ptop-30)
    ptitle_p2 = (pright, ptop)
    cv2.rectangle(img, ptitle_p1, ptitle_p2, white, -1)
    cv2.rectangle(img, ptitle_p1, ptitle_p2, black, 1)

    text = "Internal Pressures (kPa)"
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 0.7
    thickness = 2
    ptitle_p = (pleft + 10, ptop - 7)
    cv2.putText(img, text, ptitle_p, font, fontScale, black, thickness)


    pressures = [
        [df.iloc[idx]["M2-PL"], df.iloc[idx]["M2-PR"]],
        [df.iloc[idx]["M1-PL"], df.iloc[idx]["M1-PR"]]
    ]
    # targ_pressures = [
    #     [df.iloc[idx]["TP2L"], df.iloc[idx]["TP2R"]],
    #     [df.iloc[idx]["TP1L"], df.iloc[idx]["TP1R"]]
    # ]

    max_pressure = 120
    min_pressure = 98
    del_pressure = max_pressure - min_pressure

    for i in range(2):
        for j in range(2):
            width = int(pwidth / 2)
            length = int(plength / 2)
            off_x = pleft + (i * width)
            off_y = ptop + (j * length)
            pbox_top = off_y + ypad
            pbox_bot = off_y + length - ypad
            pbox_left = off_x + xpad 
            pbox_right = off_x + width - int(xpad / 1)
            pbox_p1 = (pbox_left, pbox_top)
            pbox_p2 = (pbox_right, pbox_bot)

            pb_length = pbox_bot - pbox_top
            
            ap_val = pressures[i][j]
            ap_val_x = pbox_left - 50
            tp_val = targ_pressures[i][j]
            tp_val_x = pbox_right + 5

            ap_top = pbox_bot - int(pb_length * ((ap_val - min_pressure) / del_pressure))
            ap_p1 = (pbox_left, ap_top)
            ap_p2 = (pbox_right, pbox_bot)

            tp_top = pbox_bot - int(pb_length * ((tp_val - min_pressure) / del_pressure))
            tp_p1 = (pbox_left, tp_top)
            tp_p2 = (pbox_right, tp_top)

            ap_val_p = (ap_val_x, ap_top)
            tp_val_p = (tp_val_x, tp_top)

            ap_text = str(round(ap_val, 1))
            tp_text = str(round(tp_val, 1))
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 0.5
            thickness = 2

            cv2.rectangle(img, ap_p1, ap_p2, blue, -1)
            cv2.putText(img, ap_text, ap_val_p, font, fontScale, blue, thickness)
            cv2.line(img, tp_p1, tp_p2, red, 3)
            cv2.putText(img, tp_text, tp_val_p, font, fontScale, red, thickness)
            cv2.rectangle(img, pbox_p1, pbox_p2, black, 3)

def annotate_image(data_df, index, img):
    data = np.zeros((len(fk_x)))

    actual = np.zeros((len(y_lbl)))

    idx = 0
    for i in range(index, index - (lookback + 1) * 7, -7):
        line = data_df.loc[i]

        if (i == index):
            for j in range(len(y_lbl)):
                actual[j] = line[y_lbl[j]]

        for j in range(x_labels):
            data[idx + j] = line[fk_x[j]]
            if (j <= 3):
                data[idx + j] = downscale(data[idx + j], norm_bounds.loc[0, fk_x[j]], norm_bounds.loc[1, fk_x[j]])
                
        idx += x_labels
    
    fk_pred = fkmodel.predict(data.reshape((1, len(fk_x))), verbose=0)[0]
    fk_pred = scale_data(upscale, fk_pred, fk_y).reshape((int(len(fk_y) / 2), 2))

    actual = actual.reshape((int(len(y_lbl) / 2), 2))

    ox, oy = actual[0]

    for i in range(fk_pred.shape[0]):
        fk_pred[i][0] += ox
        fk_pred[i][1] = oy - fk_pred[i][1]

    print(actual)
    
    data = actual[1::].reshape(len(ik_x))
    data = scale_data(downscale, data, ik_x).reshape(1, len(ik_x))
    print(data)
    pred_ik = ikmodel.predict(data)[0]
    print(scale_data(upscale, pred_ik, ik_y))

    # drawing stuff
    
    for i in range(actual.shape[0]):
        if i > 0:
            fk_pred[i - 1] = world2pix(fk_pred[i - 1])
            actual[i][0] += ox
            actual[i][1] = oy - actual[i][1]
        actual[i] = world2pix(actual[i])

    img = cv2.undistort(img, mtx, dist, None, newcameramtx)

    fk_pred = np.resize(fk_pred, (actual.shape))
    fk_pred = np.roll(fk_pred, 1, axis=0)
    fk_pred[0] = actual[0]

    fk_pred = fk_pred.astype(int)
    actual = actual.astype(int)

    draw_circle_line(img, actual, (0, 255, 0))
    draw_circle_line(img, fk_pred, (0, 0, 255))

    cv2.imshow("img", img)
    cv2.waitKey(1)

    return img
    

def convert_experiment(experiment_dir):
    img_dir = experiment_dir + "/imgs"
    files = os.listdir(experiment_dir)

    data_csv_file = ""
    for file in files:
        if "control_data" in file:
            data_csv_file = f"{experiment_dir}/{file}"
            break
    
    data_df = pd.read_csv(data_csv_file)

    images = []
    for i in tqdm(range(max(lookback * 7, 0), len(data_df))):
        img = cv2.imread(f"{img_dir}/img{i}.jpg")
        images.append(annotate_image(data_df, i, img))
    return images

if __name__ == "__main__":
    if not os.path.isdir(video_dir):
        os.mkdir(video_dir)
    experiments = os.listdir(experiments_dir)
    for i in range(len(experiments)):
        print(f"\n{i + 1} / {len(experiments)} : Converting {experiments[i]}")
        out = cv2.VideoWriter(f"{video_dir}/{experiments[i]}.mp4", codec, hz * speed, (1280, 720))
        images = convert_experiment(f"{experiments_dir}/{experiments[i]}")
        for img in images:
            out.write(img)
        out.release()
