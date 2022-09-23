import csv
import cv2
import numpy as np
import glob
import math
import pickle
import os
import pandas as pd
from detect import RobotDetector


# import autompc as ampc # Version: 0.2
# from autompc.sysid import MLP
# import ConfigSpace as CS
# import ast
# import sys

# sys.path.insert(0, "/Users/davidnull/phd/underwater_robot_autompc/utils") # Replace relative path to underwater_robot_autompc/utils
# import utils
# sys.path.insert(1, "/Users/davidnull/phd/underwater_robot_autompc/experiment_scripts") # Replace relative path to underwater_robot_autompc/experiment_scripts
# import generalization_experiment_01 as experiment

mint = [0, 0, 141]
#maxt = [141, 137, 255]
maxt = [133, 115, 255]
color_threshold = (np.array(mint), np.array(maxt))

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

detector = RobotDetector()

ampc_dir = "/Users/davidnull/phd/data/Acc40_Ampc_r1/"
vs_dir = "/Users/davidnull/phd/data/Acc40_Visual_Servo_r1/"
ol_dir = "/Users/davidnull/phd/data/acc40/"

proj_dir = "/Users/davidnull/phd/papers/ICRA_2023/supp_video/"
proj_name = "supplementary_video"
proj_ext = ".mp4"

size = (1280,720)
file_name = proj_dir + proj_name + proj_ext
hz = 2
speed = 4
fps = speed * hz
targ_list = [0, 19, 39]
radius = 5
red = (0, 0, 255)
green = (0, 255, 0)
orange = (0, 165, 255)
yellow = (0, 255, 255)
blue = (255, 0, 0)
white = (255, 255, 255)
black = (0, 0, 0)

dfed = pd.read_csv("./end_data.csv")

def world2pix(x, y):
        coord_3d = np.array([
            x / camera_to_markers_dist,
            y / camera_to_markers_dist,
            1
        ])
        coord_2d = np.matmul(newcameramtx, coord_3d)
        return int(coord_2d[0]), int(coord_2d[1])

def get_key(fp):
    filename = os.path.splitext(os.path.basename(fp))[0]
    int_part = filename.split()[0]
    return int(int_part)

def draw_target(img, targ=None, origin=None, color=red):
    ox = origin[0]
    oy = origin[1]
    o_pix = world2pix(ox, oy)
    cv2.circle(img, o_pix, radius, red, 3)

    tx = ox + targ[0]
    ty = oy - targ[1]
    tbox_side = 2
    tbox1x = tx - (tbox_side/2)
    tbox1y = ty - (tbox_side/2)
    tbox2x = tx + (tbox_side/2)
    tbox2y = ty + (tbox_side/2)
    tbox1 = world2pix(tbox1x, tbox1y)
    tbox2 = world2pix(tbox2x, tbox2y)
    targ_pix = world2pix(tx, ty)
    cv2.circle(img, targ_pix, 5, red, 3)
    cv2.rectangle(img, tbox1, tbox2, red, 3, -1)

    return ox, oy

# def draw_path(img, path=None, idx=0, origin=None, targ=None, color=yellow):
#     pathx = path[0]
#     pathy = path[1]
#     ox, oy = draw_target(img, targ=targ, origin=origin)

#     for j in range(idx+1):
#         if j >= len(pathx):
#             break
#         p1x = ox + float(pathx[j])
#         p1y = oy - float(pathy[j])
#         p1 = world2pix(p1x, p1y)

#         if j == 0:
#             cv2.circle(img, p1, 5, color, 3)
        
#         if j > 0 and j < (len(pathx)-1):
#             p2x = ox + float(pathx[j+1])
#             p2y = oy - float(pathy[j+1])
#             p2 = world2pix(p2x, p2y)
#             cv2.line(img, p1, p2, color, thickness=3)
#             if j+1 == idx:
#                 cv2.circle(img, p2, 5, color, 3)
#         elif j == len(pathx)-1:
#             cv2.circle(img, p1, 5, color, 3)
#     return img

def handle_ol_run(run_idx, out):
    ol_run_dir = ol_dir + "/" + str(run_idx) + "/simple_comb/run0/"
    imgs_dir = ol_run_dir + "/imgs/"
    csv_file = glob.glob(ol_run_dir + '/*.csv')[0]
    df = pd.read_csv(csv_file)

    with open('../softwater_app/simple_controller_old.p', 'rb') as f:
        control_pressures = pickle.load(f)['comb']

    data_arr = csv_file.split("/")[-1].split(".")[0].split("_")
    targ = (float(data_arr[-2]), float(data_arr[-1]))

    data1 = dfed.loc[dfed['x'] == targ[0]]
    data = data1.loc[data1['y'] == targ[1]]

    # ox = data["origx_ampc"].iloc[0]
    # oy = data["origy_ampc"].iloc[0]
    # origin = (ox, oy)

    pathx = " ".join(data["simp_pathx"].iloc[0][1:-1].split("\n")).split()
    pathy = " ".join(data["simp_pathy"].iloc[0][1:-1].split("\n")).split()
    # ol_path = (pathx, pathy)
    ol_path = [[],[]]
    origin = (0,0)
    xee_prev = []
    time_outside_g = -0.5
    for idx, filename in enumerate(sorted(glob.glob(imgs_dir + '/*.jpg'), key=get_key)):
        if idx == len(pathx):
            print("exceeded")
            break
        print(filename)
        img = cv2.imread(filename)
        img = cv2.resize(img, size)
        tracking, camera_image, tracker_image = detector.detect(img)
        m = detector.pix2world(detector.tracker.objects)
        if idx == 0:
            ox = m[0][0]
            oy = m[0][1]
            origin = (ox, oy)
        
        img = cv2.undistort(img, mtx, dist, None, newcameramtx)

        for i in range(1,10):
            mx = ox + df.iloc[idx]["M" + str(i) + "X"]
            my = oy - df.iloc[idx]["M" + str(i) + "Y"]
            m = world2pix(mx, my)
            cv2.circle(img, m, radius, red, 3)
        draw_target(img, targ=targ, origin=origin)
        
        xw = ox + df.iloc[idx]["M10X"]
        yw = oy - df.iloc[idx]["M10Y"]
        tx = ox + targ[0]
        ty = oy - targ[1]
        xee = world2pix(xw, yw)
        
        ol_path[0].append(df.iloc[idx]["M10X"])
        ol_path[1].append(df.iloc[idx]["M10Y"])

        for j in range(len(xee_prev)):
            if j == 0:
                cv2.circle(img, xee_prev[j], radius, yellow, 3)
            p1 = xee_prev[j]
            if j < len(xee_prev)-1:
                p2 = xee_prev[j+1]
            else:
                p2 = xee
            cv2.line(img, p1, p2, yellow, thickness=3)
        xee_prev.append(xee)

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
            [df.iloc[idx]["M2-PL"], df.iloc[idx]["M1-PL"]],
            [df.iloc[idx]["M2-PR"], df.iloc[idx]["M1-PR"]]
        ]
        tpres = control_pressures[targ]
        targ_pressures = [
            [tpres[2], tpres[0]],
            [tpres[3], tpres[1]]
        ]

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

        error = (tx - xw, ty - yw)
        error_round = (round(error[0], 2), round(error[1], 2))
        distance = round(math.sqrt(error[0] * error[0] + error[1] * error[1]), 2)
        targ_round =      (round(tx - ox, 2), round(oy - ty, 2))
        xee_round =       (round(xw - ox, 2), round(oy - yw, 2))

        if abs(error[0]) > 1 or abs(error[1]) > 1:
            time_outside_g += 0.5

        title = []
        title.append("Open Loop IK")
        title.append(str(speed) + "x")

        details = []
        # details.append("DETAILS: Open Loop IK")
        # details.append("Playback Speed: " + str(speed) + "x")
        # details.append("Run IDX:    " + str(run_idx))
        details.append("Time Outside Goal Reg. (s): " + str(time_outside_g))
        details.append("Dist (cm):       " + str(distance))
        details.append("Xee (cm):        " + str(xee_round))
        details.append("Target (cm):     " + str(targ_round))
        details.append("Error (cm):      " + str(error_round))
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 0.6
        thickness = 2
        dp_x = 5
        dp_y = 590
        dp_del = 20
        cv2.rectangle(img, (0,dp_y-20), (335,730), white, -1)
        for i, text in enumerate(details):
            details_p = (dp_x, dp_y + (dp_del * i)) 
            color = black
            if "Xee" in text:
                color = black
            elif "Target" in text:
                color = red
            cv2.putText(img, text, details_p, font, fontScale, color, thickness)

        dp_x = 15
        dp_y = 45
        dp_del = 40
        fontScale = 1
        cv2.rectangle(img, (0,0), (250,110), white, -1)
        cv2.rectangle(img, (100,67), (200,83), yellow, -1)
        cv2.rectangle(img, (100,67), (200,83), black, 1)
        for i, text in enumerate(title):
            details_p = (dp_x, dp_y + (dp_del * i)) 
            color = black
            cv2.putText(img, text, details_p, font, fontScale, color, thickness)
        


        cv2.circle(img, xee, radius, yellow, 3)

        out.write(img)

    return ol_path

def get_run_dirs(home_dir, run_idx):
    run_dirs = glob.glob(home_dir + "/*")
    for rd in run_dirs:
        if (" IDX" + str(run_idx) + " ") in rd:
            run_dir = rd + "/"
            break
    for fname in glob.glob(run_dir + '/*.csv'):
        if "debug_log" not in fname:
            csv_file = fname
            break
    imgs_dir = run_dir + "imgs/"
    return run_dir, csv_file, imgs_dir

def draw_target_vs(img, tw=None, targ=None, adjtarg=None, orig=None, color=red):
    cv2.circle(img, orig, radius, red, 3)
    tx = tw[0]
    ty = tw[1]
    tbox_side = 2
    tbox1x = tx - (tbox_side/2)
    tbox1y = ty - (tbox_side/2)
    tbox2x = tx + (tbox_side/2)
    tbox2y = ty + (tbox_side/2)
    tbox1 = world2pix(tbox1x, tbox1y)
    tbox2 = world2pix(tbox2x, tbox2y)
    cv2.circle(img, targ, radius, black, 3)
    cv2.circle(img, adjtarg, radius, red, 3)
    cv2.rectangle(img, tbox1, tbox2, red, 3)
    return img

def draw_prev_path(img, path, orig, color):
    ox = orig[0]
    oy = orig[1]
    pathx = path[0]
    pathy = path[1]
    for i in range(1, len(pathx)):
        pathx[i-1] = float(pathx[i-1])
        pathy[i-1] = float(pathy[i-1])
        pathx[i] = float(pathx[i])
        pathy[i] = float(pathy[i])
        p1x = ox + pathx[i-1]
        p1y = oy - pathy[i-1]
        p1 = world2pix(p1x, p1y)
        p2x = ox + pathx[i]
        p2y = oy - pathy[i]
        p2 = world2pix(p2x, p2y)
        cv2.line(img, p1, p2, color, thickness=3)

    p1x = ox + pathx[0]
    p1y = oy - pathy[0]
    p1 = world2pix(p1x, p1y)
    p2x = ox + pathx[-1]
    p2y = oy - pathy[-1]
    p2 = world2pix(p2x, p2y)
    
    cv2.circle(img, p1, 5, color, 3)
    cv2.circle(img, p2, 5, color, 3)
    
        

def handle_vs_run(run_idx, ol_path, out):
    run_dir, csv_file, imgs_dir = get_run_dirs(vs_dir, run_idx)
    df = pd.read_csv(csv_file)

    xee_prev = []
    vs_path = [[],[]]

    time_outside_g = -0.5
    for idx, filename in enumerate(sorted(glob.glob(imgs_dir + '/*.jpg'), key=os.path.getmtime)):
        print(filename)
        img = cv2.imread(filename)
        img = cv2.undistort(img, mtx, dist, None, newcameramtx)
        oxw = df.iloc[idx]["ORIGX"]
        oyw = df.iloc[idx]["ORIGY"]
        origin = (oxw, oyw)
        for i in range(1,10):
            mx = oxw + df.iloc[idx]["M" + str(i) + "X"]
            my = oyw - df.iloc[idx]["M" + str(i) + "Y"]
            m = world2pix(mx, my)
            cv2.circle(img, m, radius, red, 3)
        draw_prev_path(img, ol_path, origin, yellow)
        xw = oxw + df.iloc[idx]["XEEX"]
        yw = oyw - df.iloc[idx]["XEEY"]
        tx = oxw + df.iloc[idx]["TARGX"]
        ty = oyw - df.iloc[idx]["TARGY"]
        tw = (tx, ty)
        atx = oxw + df.iloc[idx]["ADJ_TARGX"]
        aty = oyw - df.iloc[idx]["ADJ_TARGY"]
        
        vs_path[0].append(df.iloc[idx]["XEEX"])
        vs_path[1].append(df.iloc[idx]["XEEY"])

        xee = world2pix(xw, yw)
        orig = world2pix(oxw, oyw)
        targ = world2pix(tx, ty)
        adjtarg = world2pix(atx, aty)
        img = draw_target_vs(img, tw=tw, targ=targ, adjtarg=adjtarg, orig=orig)
        #cv2.drawMarker(img, orig, red, cv2.MARKER_CROSS, thickness=3)

        for j in range(len(xee_prev)):
            if j == 0:
                cv2.circle(img, xee_prev[j], radius, green, 3)
            p1 = xee_prev[j]
            if j < len(xee_prev)-1:
                p2 = xee_prev[j+1]
            else:
                p2 = xee
            cv2.line(img, p1, p2, green, thickness=3)
        xee_prev.append(xee)


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
            [df.iloc[idx]["M2-PL"], df.iloc[idx]["M1-PL"]],
            [df.iloc[idx]["M2-PR"], df.iloc[idx]["M1-PR"]]
        ]
        targ_pressures = [
            [df.iloc[idx]["TP2L"], df.iloc[idx]["TP1L"]],
            [df.iloc[idx]["TP2R"], df.iloc[idx]["TP1R"]]
        ]

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

        # error =     (df.iloc[idx]["ERRORX"    ], df.iloc[idx]["ERRORY"      ])
        error = (tx - xw, ty - yw)
        error_round = (round(error[0], 2), round(error[1], 2))
        distance = round(math.sqrt(error[0] * error[0] + error[1] * error[1]), 2)
        targ_round =      (round(tx - oxw, 2), round(oyw - ty, 2))
        adjtarg_round =   (round(atx- oxw, 2), round(oyw - aty,2))
        xee_round =       (round(xw - oxw, 2), round(oyw - yw, 2))
        int_error = (round(df.iloc[idx]["INT_ERRX"  ], 2), round(df.iloc[idx]["INT_ERRY"    ], 2))
        P =     (round(df.iloc[idx]["PX"  ], 2), round(df.iloc[idx]["PY"    ], 2))
        I =     (round(df.iloc[idx]["IX"  ], 2), round(df.iloc[idx]["IY"    ], 2))
        KP =    (round(df.iloc[idx]["KPX" ], 2), round(df.iloc[idx]["KPY"   ], 2))
        KI =    (round(df.iloc[idx]["KIX" ], 2), round(df.iloc[idx]["KIY"   ], 2))

        if abs(error[0]) > 1 or abs(error[1]) > 1:
            time_outside_g += 0.5

        title = []
        title.append("Visual Servo")
        title.append(str(speed) + "x")
        

        details = []
        # details.append("DETAILS: Visual Servo")
        # details.append("Playback Speed: " + str(speed) + "x")
        # details.append("Run IDX:    " + str(run_idx))
        details.append("Time Outside Goal Reg. (s): " + str(time_outside_g))
        details.append("Dist (cm):       " + str(distance))
        details.append("Xee (cm):        " + str(xee_round))
        details.append("Target (cm):     " + str(targ_round))
        details.append("Adj Target (cm): " + str(adjtarg_round))
        details.append("Error (cm):      " + str(error_round))
        # details.append("Int Error:  " + str(int_error))
        # details.append("Kp:         " + str(KP))
        # details.append("P:          " + str(P))
        # details.append("Ki:         " + str(KI))
        # details.append("I:          " + str(I))
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 0.6
        thickness = 2
        dp_x = 5
        dp_y = 590
        dp_del = 20
        cv2.rectangle(img, (0,dp_y-20), (335,730), white, -1)
        for i, text in enumerate(details):
            details_p = (dp_x, dp_y + (dp_del * i)) 
            color = black
            if "Xee" in text:
                color = green
            elif "Adj Target" in text:
                color = red
            elif "Target" in text:
                color = black
            cv2.putText(img, text, details_p, font, fontScale, color, thickness)

        dp_x = 15
        dp_y = 45
        dp_del = 40
        fontScale = 1
        cv2.rectangle(img, (0,0), (250,110), white, -1)
        cv2.rectangle(img, (100,67), (200,83), green, -1)
        cv2.rectangle(img, (100,67), (200,83), black, 1)
        for i, text in enumerate(title):
            details_p = (dp_x, dp_y + (dp_del * i)) 
            color = black
            cv2.putText(img, text, details_p, font, fontScale, color, thickness)

        cv2.circle(img, xee, radius, green, 3)
        # cv2.circle(img, targ, radius, green, 3)
        # cv2.circle(img, adjtarg, radius, blue, 3)
        
        out.write(img)

    return vs_path

def draw_target_ampc(img, tw=None, targ=None, orig=None, color=red):
    cv2.circle(img, orig, radius, red, 3)
    tx = tw[0]
    ty = tw[1]
    tbox_side = 2
    tbox1x = tx - (tbox_side/2)
    tbox1y = ty - (tbox_side/2)
    tbox2x = tx + (tbox_side/2)
    tbox2y = ty + (tbox_side/2)
    tbox1 = world2pix(tbox1x, tbox1y)
    tbox2 = world2pix(tbox2x, tbox2y)
    cv2.circle(img, targ, radius, red, 3)
    cv2.rectangle(img, tbox1, tbox2, red, 3)
    return img

def handle_ampc_run(run_idx, ol_path, vs_path, out):
    run_dir, csv_file, imgs_dir = get_run_dirs(ampc_dir, run_idx)
    df = pd.read_csv(csv_file)

    # system = utils.get_system_ver2()
    # trajs = utils.load_trajs(experiment_names=experiment.experiment_names, traj_converter=utils.df_to_traj_ver2, folderName=experiment.datasetFolder)
    # all_goals = experiment.get_targets()+[[-13,25],[-13,27],[-13,29],[-11,31],[-9,33],[-7,35],[-5,37],[-3,39],[-1,39],[1,39],[3,39],[5,37],[7,35],[9,33],[11,31],[13,29],[13,27],[13,25]]
    # csv = csv_file
    # result_path = os.path.dirname(os.path.realpath(csv))
    # goal = [int(csv.split('_')[-2]), int(csv.split('_')[-1][:-4])]
    # goal_idx = all_goals.index(goal)
    # task = experiment.init_task(goal)
    # df = pd.read_csv(csv)
    # debug_df = pd.read_csv(os.path.join(result_path, 'debug_log.csv'))
    # traj = ampc.Trajectory(system, df[system.observations].to_numpy(), df[system.controls].to_numpy())
    # robot_intermediate_trajs = [] # This is the list of planned trajectories for every timestep

    xee_prev = []

    time_outside_g = -0.5
    for idx, filename in enumerate(sorted(glob.glob(imgs_dir + '/*.jpg'), key=os.path.getmtime)):
        print(filename)
        img = cv2.imread(filename)
        img = cv2.undistort(img, mtx, dist, None, newcameramtx)
        oxw = df.iloc[idx]["ORIGX"]
        oyw = df.iloc[idx]["ORIGY"]
        origin = (oxw, oyw)
        for i in range(1,10):
            mx = oxw + df.iloc[idx]["M" + str(i) + "X"]
            my = oyw - df.iloc[idx]["M" + str(i) + "Y"]
            m = world2pix(mx, my)
            cv2.circle(img, m, radius, red, 3)
        draw_prev_path(img, ol_path, origin, yellow)
        draw_prev_path(img, vs_path, origin, green)
        xw = oxw + df.iloc[idx]["XEEX"]
        yw = oyw - df.iloc[idx]["XEEY"]
        tx = oxw + df.iloc[idx]["TARGX"]
        ty = oyw - df.iloc[idx]["TARGY"]
        tw = (tx,ty)



        # obs = df.loc[idx,system.observations].to_numpy()
        # ctrl = df.loc[idx,system.controls].to_numpy()
        # states = debug_df.States[idx//4]
        # ctrls = debug_df.Ctrls[idx//4]
        # states = np.array(ast.literal_eval(states))
        # ctrls = np.vstack([np.array(ast.literal_eval(ctrls)),np.zeros((1, system.ctrl_dim))])
        # robot_intermediate_trajs.append(ampc.Trajectory(system, obs=states[idx%4:], ctrls=ctrls[idx%4:]))
        # print(robot_intermediate_trajs)


        xee = world2pix(xw, yw)
        orig = world2pix(oxw, oyw)
        targ = world2pix(tx, ty)
        img = draw_target_ampc(img, tw=tw, targ=targ, orig=orig)
        # cv2.drawMarker(img, orig, red, cv2.MARKER_CROSS, thickness=3)

        for j in range(len(xee_prev)):
            if j == 0:
                cv2.circle(img, xee_prev[j], radius, blue, 3)

            p1 = xee_prev[j]
            if j < len(xee_prev)-1:
                p2 = xee_prev[j+1]
            else:
                p2 = xee
            cv2.line(img, p1, p2, blue, thickness=3)
        xee_prev.append(xee)


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
            [df.iloc[idx]["M2-PL"], df.iloc[idx]["M1-PL"]],
            [df.iloc[idx]["M2-PR"], df.iloc[idx]["M1-PR"]]
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
                tp_val_x = pbox_right + 5

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

        error =     (df.iloc[idx]["ERRORX"    ], df.iloc[idx]["ERRORY"      ])
        error_round = (round(error[0], 2), round(error[1], 2))
        distance = round(math.sqrt(error[0] * error[0] + error[1] * error[1]), 2)
        targ_round =      (round(tx - oxw, 2), round(oyw - ty, 2))
        xee_round =       (round(xw - oxw, 2), round(oyw - yw, 2))

        if abs(error[0]) > 1 or abs(error[1]) > 1:
            time_outside_g += 0.5
        
        title = []
        title.append("AutoMPC")
        title.append(str(speed) + "x")

        details = []
        # details.append("DETAILS: AutoMPC")
        # details.append("Playback Speed: " + str(speed) + "x")
        # details.append("Run IDX:    " + str(run_idx))
        details.append("Time Outside Goal Reg. (s): " + str(time_outside_g))
        details.append("Dist (cm):       " + str(distance))
        details.append("Xee (cm):        " + str(xee_round))
        details.append("Target (cm):     " + str(targ_round))
        details.append("Error (cm):      " + str(error_round))
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 0.6
        thickness = 2
        dp_x = 5
        dp_y = 590
        dp_del = 20
        cv2.rectangle(img, (0,dp_y-20), (335,730), white, -1)
        for i, text in enumerate(details):
            details_p = (dp_x, dp_y + (dp_del * i)) 
            color = black
            if "Xee" in text:
                color = blue
            elif "Target" in text:
                color = red
            cv2.putText(img, text, details_p, font, fontScale, color, thickness)

        dp_x = 15
        dp_y = 45
        dp_del = 40
        fontScale = 1
        cv2.rectangle(img, (0,0), (250,110), white, -1)
        cv2.rectangle(img, (100,67), (200,83), blue, -1)
        cv2.rectangle(img, (100,67), (200,83), black, 1)
        for i, text in enumerate(title):
            details_p = (dp_x, dp_y + (dp_del * i)) 
            color = black
            cv2.putText(img, text, details_p, font, fontScale, color, thickness)

        cv2.circle(img, xee, radius, blue, 3)
        # cv2.circle(img, targ, radius, green, 3)
        
        out.write(img)

    ampc_path = []
    return ampc_path

def create_video(targ, out):
    ol_path = handle_ol_run(targ, out)
    vs_path = handle_vs_run(targ, ol_path, out)
    ampc_path = handle_ampc_run(targ, ol_path, vs_path, out)

if __name__ == "__main__":
    mp4_codec = cv2.VideoWriter_fourcc(*'X264')
    avi_codec = cv2.VideoWriter_fourcc(*'DIVX')
    out = cv2.VideoWriter(file_name, mp4_codec, fps, size)

    for targ in targ_list:
        create_video(targ, out)

    out.release()
