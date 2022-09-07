import csv
import cv2
import numpy as np
import glob
import math
import os
import pandas as pd

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

inv_camera_mtx = np.linalg.inv(newcameramtx)

dist = np.array([[0.19210016, -0.4423498, 0.00093771, -0.00542759, 0.25832642 ]])

camera_to_markers_dist = 57.055 #cm

data_dir = "/Users/davidnull/phd/data/Acc40_AutoMPC_8-26-22_tests/"
proj_dir = data_dir + "/analysis/"
proj_name = "ampc0"

size = (1280,720)
file_name = proj_dir + proj_name + ".mp4"
hz = 2
speed = 3
fps = speed * hz

def world2pix(x, y):
        coord_3d = np.array([
            x / camera_to_markers_dist,
            y / camera_to_markers_dist,
            1
        ])
        coord_2d = np.matmul(newcameramtx, coord_3d)
        return int(coord_2d[0]), int(coord_2d[1])

def handle_run(run_dir, run_idx, out):
    csv_file = glob.glob(run_dir + '/*.csv')[0]
    imgs_dir = run_dir + "imgs/"
    df = pd.read_csv(csv_file)
    
    radius = 5
    red = (0, 0, 255)
    green = (0, 255, 0)
    blue = (255, 0, 0)
    white = (255, 255, 255)
    black = (0, 0, 0)

    xee_prev = []

    for idx, filename in enumerate(sorted(glob.glob(imgs_dir + '/*.jpg'), key=os.path.getmtime)):
        img = cv2.imread(filename)
        img = cv2.undistort(img, mtx, dist, None, newcameramtx)
        oxw = df.iloc[idx]["ORIGX"]
        oyw = df.iloc[idx]["ORIGY"]
        xw = oxw + df.iloc[idx]["XEEX"]
        yw = oyw - df.iloc[idx]["XEEY"]
        tx = oxw + df.iloc[idx]["TARGX"]
        ty = oyw - df.iloc[idx]["TARGY"]
        # atx = oxw + df.iloc[idx]["ADJ_TARGX"]
        # aty = oyw - df.iloc[idx]["ADJ_TARGY"]
        

        xee = world2pix(xw, yw)
        orig = world2pix(oxw, oyw)
        targ = world2pix(tx, ty)
        # adjtarg = world2pix(atx, aty)
        cv2.drawMarker(img, orig, red, cv2.MARKER_CROSS, thickness=3)

        for j in range(len(xee_prev)):
            p1 = xee_prev[j]
            if j < len(xee_prev)-1:
                p2 = xee_prev[j+1]
            else:
                p2 = xee
            cv2.line(img, p1, p2, red, thickness=3)
        xee_prev.append(xee)

        for i in range(1,10):
            mx = oxw + df.iloc[idx]["M" + str(i) + "X"]
            my = oyw - df.iloc[idx]["M" + str(i) + "Y"]
            m = world2pix(mx, my)
            cv2.circle(img, m, radius, red, 3)

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
                # tp_val = targ_pressures[i][j]
                # tp_val_x = pbox_right + 5

                ap_top = pbox_bot - int(pb_length * ((ap_val - min_pressure) / del_pressure))
                ap_p1 = (pbox_left, ap_top)
                ap_p2 = (pbox_right, pbox_bot)

                # tp_top = pbox_bot - int(pb_length * ((tp_val - min_pressure) / del_pressure))
                # tp_p1 = (pbox_left, tp_top)
                # tp_p2 = (pbox_right, tp_top)

                ap_val_p = (ap_val_x, ap_top)
                # tp_val_p = (tp_val_x, tp_top)

                ap_text = str(round(ap_val, 1))
                # tp_text = str(round(tp_val, 1))
                font = cv2.FONT_HERSHEY_SIMPLEX
                fontScale = 0.5
                thickness = 2

                cv2.rectangle(img, ap_p1, ap_p2, blue, -1)
                cv2.putText(img, ap_text, ap_val_p, font, fontScale, blue, thickness)
                # cv2.line(img, tp_p1, tp_p2, red, 3)
                # cv2.putText(img, tp_text, tp_val_p, font, fontScale, red, thickness)
                cv2.rectangle(img, pbox_p1, pbox_p2, black, 3)

        error =     (round(df.iloc[idx]["ERRORX"    ], 2), round(df.iloc[idx]["ERRORY"      ], 2))
        # rmse = round(math.sqrt(error[0] * error[0] + error[1] * error[1]), 2)
        rmse = round(df.iloc[idx]["RMSE"], 2)
        targ_round =      (round(tx - oxw, 2), round(oyw - ty, 2))
        # adjtarg_round =   (round(atx- oxw, 2), round(oyw - aty,2))
        xee_round =       (round(xw - oxw, 2), round(oyw - yw, 2))
        # int_error = (round(df.iloc[idx]["INT_ERRX"  ], 2), round(df.iloc[idx]["INT_ERRY"    ], 2))
        # P =     (round(df.iloc[idx]["PX"  ], 2), round(df.iloc[idx]["PY"    ], 2))
        # I =     (round(df.iloc[idx]["IX"  ], 2), round(df.iloc[idx]["IY"    ], 2))
        # KP =    (round(df.iloc[idx]["KPX" ], 2), round(df.iloc[idx]["KPY"   ], 2))
        # KI =    (round(df.iloc[idx]["KIX" ], 2), round(df.iloc[idx]["KIY"   ], 2))

        details = []
        # details.append("DETAILS")
        details.append("AutoMPC DETAILS")
        details.append("Playback Speed: " + str(speed) + "x")
        details.append("Run IDX:    " + str(run_idx))
        details.append("RMSE (cm):       " + str(rmse))
        details.append("Xee (cm):        " + str(xee_round))
        details.append("Target (cm):     " + str(targ_round))
        # details.append("Adj Target (cm): " + str(adjtarg_round))
        details.append("Error:      " + str(error))
        # details.append("Int Error:  " + str(int_error))
        # details.append("Kp:         " + str(KP))
        # details.append("P:          " + str(P))
        # details.append("Ki:         " + str(KI))
        # details.append("I:          " + str(I))
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 0.6
        thickness = 2
        dp_x = 5
        dp_y = 470
        dp_del = 20
        cv2.rectangle(img, (0,dp_y-20), (320,730), white, -1)
        for i, text in enumerate(details):
            details_p = (dp_x, dp_y + (dp_del * i)) 
            color = black
            if "Xee" in text:
                color = red
            elif "Adj Target" in text:
                color = blue
            elif "Target" in text:
                color = green
            cv2.putText(img, text, details_p, font, fontScale, color, thickness)

        cv2.circle(img, xee, radius, red, 3)
        cv2.circle(img, targ, radius, green, 3)
        # cv2.circle(img, adjtarg, radius, blue, 3)
        
        out.write(img)

if __name__ == "__main__":

    mp4_codec = cv2.VideoWriter_fourcc(*'X264')
    avi_codec = cv2.VideoWriter_fourcc(*'DIVX')
    out = cv2.VideoWriter(file_name, mp4_codec, fps, size)
    #Visual_Servo IDX0 14-33-53 8-23-2022/

    # run_dirs = glob.glob(data_dir + "/*")
    # run_num = 40
    # for i in range(run_num):
    #     run_dir = ""
    #     for rd in run_dirs:
    #         if (" IDX" + str(i) + " ") in rd:
    #             run_dir = rd + "/"
    #             break
    #     print(run_dir)
    #     handle_run(run_dir, i, out)
    # run_dirs = [
    #     data_dir + "/Auto_MPC IDX0 8-13-36 8-26-2022/",
    #     data_dir + "/Auto_MPC IDX9 8-42-23 8-26-2022/"
    # ]
    # run_dirs = [
    #     data_dir + "/Auto_MPC IDX0 9-20-52 8-26-2022/",
    #     data_dir + "/Auto_MPC IDX9 9-0-35 8-26-2022/"
    # ]
    run_dirs = [
        data_dir + "/Auto_MPC IDX38 10-0-2 8-26-2022/",
        data_dir + "/Auto_MPC IDX38 9-38-22 8-26-2022/"
    ]
    handle_run(run_dirs[0], 38, out)
    handle_run(run_dirs[1], 38, out)

    out.release()