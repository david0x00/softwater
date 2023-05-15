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

ol_ood_dir = "/Users/davidnull/phd/data/Acc40_Open_Loop_OOD_r1/"
vs_ood_dir = "/Users/davidnull/phd/data/Acc40_Visual_Servo_OOD_r1/"
trpo_ood_dir = "/Users/davidnull/phd/data/Acc40_TRPO_OOD_r1/"
cql_ood_dir = "/Users/davidnull/phd/data/Acc40_CQL_OOD_r1/"
ampc_ood_dir = "/Users/davidnull/phd/data/Acc40_Ampc_OOD_r1/"

ol_dir = "/Users/davidnull/phd/data/acc40/"
vs_dir = "/Users/davidnull/phd/data/Acc40_Visual_Servo_r1/"
trpo_dir = "/Users/davidnull/phd/data/Acc40_TRPO_r1/"
cql_dir = "/Users/davidnull/phd/data/Acc40_CQL_r1/"
ampc_dir = "/Users/davidnull/phd/data/Acc40_Ampc_r1/"

def in_goal(curr, targ):
    x = curr[0]
    y = curr[1]
    xt = targ[0]
    yt = targ[1]

    if (x >= xt - 1.0) and (x <= xt + 1.0) and (y >= yt - 1.0) and (y <= yt + 1.0):
        return True
    else:
        return False


def get_details(directory, ood=False):
    for filename in glob.glob(directory + "*.csv"):
        if "debug_log" not in filename:
            data_arr = filename.split("/")[-1].split(".")[0].split("_")
            targ = (float(data_arr[-2]), float(data_arr[-1]))
            df = pd.read_csv(filename)
            end_targ = (float(df["M10X"].iloc[-1]), float(df["M10Y"].iloc[-1]))
            #rms = mean_squared_error(targ, end_targ, squared=False)
            dist = math.sqrt((targ[0] - end_targ[0])*(targ[0] - end_targ[0]) + (targ[1] - end_targ[1])*(targ[1] - end_targ[1]))
            # rms = df["RMSE"].iloc[-1]
            # print("Goal: " + str(targ) + ", Actual: " + str(end_targ) + ", Dist: " + str(dist) + " cm")
            
            m10x = df["M10X"].values
            m10y = df["M10Y"].values

            if ampc_dir in directory:
                origx = float(df["ORIGX"].iloc[-1])
                origy = float(df["ORIGY"].iloc[-1])
            elif vs_dir in directory:
                origx = float(df["ORIGX"].iloc[-1])
                origy = float(df["ORIGY"].iloc[-1])
            else:
                origx = None
                origy = None

            start_time = df["TIME"].iloc[0]
            prev_time = start_time
            
            reached = False
            reached_end = in_goal(end_targ, targ)
            time_first_reached = 0.0
            time_inside_goal = 0.0
            estopped = False

            if ood:
                time_outside_goal = 70.0
            else:
                time_outside_goal = 50.0

            for index, row in df.iterrows():
                curr_time = row["TIME"]
                elapsed_time = curr_time - start_time
                if elapsed_time > time_outside_goal:
                    break

                pressures = [row["M1-PL"], row["M1-PR"], row["M2-PL"], row["M2-PR"]]
                for p in pressures:
                    if p > 118.0:
                        estopped = True

                pos = (row["M10X"], row["M10Y"])
                if in_goal(pos, targ):
                    if (reached == False):
                        time_first_reached = curr_time - start_time
                        reached = True
                    time_inside_goal += curr_time - prev_time
                prev_time = curr_time
            
            time_outside_goal = time_outside_goal - time_inside_goal
            if time_outside_goal < 0:
                time_outside_goal = 0
            
            if estopped:
                reached_end = False
            
            return targ, end_targ, dist, m10x, m10y, origx, origy, reached, reached_end, time_first_reached, time_inside_goal, time_outside_goal, estopped

data = {}

def add_data(data_dir, prefix, ood=False):
    for targ_dir in glob.glob(data_dir + "/*"):
        details = get_details(targ_dir + "/", ood)
        if details != None:
            targ, end_targ, dist, m10x, m10y, origx, origy, reached, reached_end, time_first_reached, time_inside_goal, time_outside_goal, estopped = details
            if not (targ in data.keys()):
                data[targ] = {}
            data[targ][prefix + "_end"] = end_targ
            data[targ][prefix + "_dist"] = dist
            data[targ][prefix + "_pathx"] = m10x
            data[targ][prefix + "_pathy"] = m10y
            data[targ]["origx_" + prefix] = origx
            data[targ]["origy_" + prefix] = origy
            data[targ][prefix + "_reached"] = reached
            data[targ][prefix + "_reached_end"] = reached_end
            data[targ][prefix + "_time_first_reached"] = time_first_reached
            data[targ][prefix + "_time_inside_goal"] = time_inside_goal
            data[targ][prefix + "_time_outside_goal"] = time_outside_goal
            data[targ][prefix + "_estopped"] = estopped

add_data(ampc_dir, "ampc")
add_data(vs_dir, "vs")
add_data(trpo_dir, "trpo")
add_data(cql_dir, "cql")

add_data(ol_ood_dir, "simp", ood=True)
add_data(ampc_ood_dir, "ampc", ood=True)
add_data(vs_ood_dir, "vs", ood=True)
add_data(trpo_ood_dir, "trpo", ood=True)
add_data(cql_ood_dir, "cql", ood=True)



# for targ_dir in glob.glob(ampc_dir + "/*"):
#     prefix = "ampc"
#     details = get_details(targ_dir + "/")
#     if details != None:
#         targ, end_targ, dist, m10x, m10y, origx, origy, reached, reached_end, time_first_reached, time_inside_goal, time_outside_goal, estopped = details
#         data[targ] = {
#             "targ": targ,
#             prefix + "_end": end_targ,
#             prefix + "_dist": dist,
#             prefix + "_pathx": m10x,
#             prefix + "_pathy": m10y,
#             "origx_" + prefix: origx,
#             "origy_" + prefix: origy,
#             prefix + "_reached": reached,
#             prefix + "_reached_end": reached_end,
#             prefix + "_time_first_reached": time_first_reached,
#             prefix + "_time_inside_goal": time_inside_goal,
#             prefix + "_time_outside_goal": time_outside_goal,
#             prefix + "_estopped": estopped
#         }

# for targ_dir in glob.glob(vs_dir + "/*"):
#     prefix = "vs"
#     details = get_details(targ_dir + "/")
#     if details != None:
#         targ, end_targ, dist, m10x, m10y, origx, origy, reached, reached_end, time_first_reached, time_inside_goal, time_outside_goal, estopped = details
#         data[targ][prefix + "_end"] = end_targ
#         data[targ][prefix + "_dist"] = dist
#         data[targ][prefix + "_pathx"] = m10x
#         data[targ][prefix + "_pathy"] = m10y
#         data[targ]["origx_" + prefix] = origx
#         data[targ]["origy_" + prefix] = origy
#         data[targ][prefix + "_reached"] = reached
#         data[targ][prefix + "_reached_end"] = reached_end
#         data[targ][prefix + "_time_first_reached"] = time_first_reached
#         data[targ][prefix + "_time_inside_goal"] = time_inside_goal
#         data[targ][prefix + "_time_outside_goal"] = time_outside_goal
#         data[targ][prefix + "_estopped"] = estopped

# for targ_dir in glob.glob(trpo_dir + "/*"):
#     prefix = "trpo"
#     details = get_details(targ_dir + "/")
#     if details != None:
#         targ, end_targ, dist, m10x, m10y, origx, origy, reached, reached_end, time_first_reached, time_inside_goal, time_outside_goal, estopped = details
#         data[targ][prefix + "_end"] = end_targ
#         data[targ][prefix + "_dist"] = dist
#         data[targ][prefix + "_pathx"] = m10x
#         data[targ][prefix + "_pathy"] = m10y
#         data[targ]["origx_" + prefix] = origx
#         data[targ]["origy_" + prefix] = origy
#         data[targ][prefix + "_reached"] = reached
#         data[targ][prefix + "_reached_end"] = reached_end
#         data[targ][prefix + "_time_first_reached"] = time_first_reached
#         data[targ][prefix + "_time_inside_goal"] = time_inside_goal
#         data[targ][prefix + "_time_outside_goal"] = time_outside_goal
#         data[targ][prefix + "_estopped"] = estopped

# for targ_dir in glob.glob(cql_dir + "/*"):
#     prefix = "cql"
#     details = get_details(targ_dir + "/")
#     if details != None:
#         targ, end_targ, dist, m10x, m10y, origx, origy, reached, reached_end, time_first_reached, time_inside_goal, time_outside_goal, estopped = details
#         data[targ][prefix + "_end"] = end_targ
#         data[targ][prefix + "_dist"] = dist
#         data[targ][prefix + "_pathx"] = m10x
#         data[targ][prefix + "_pathy"] = m10y
#         data[targ]["origx_" + prefix] = origx
#         data[targ]["origy_" + prefix] = origy
#         data[targ][prefix + "_reached"] = reached
#         data[targ][prefix + "_reached_end"] = reached_end
#         data[targ][prefix + "_time_first_reached"] = time_first_reached
#         data[targ][prefix + "_time_inside_goal"] = time_inside_goal
#         data[targ][prefix + "_time_outside_goal"] = time_outside_goal
#         data[targ][prefix + "_estopped"] = estopped

for targ_dir in glob.glob(ol_dir + "/*"):
    prefix = "simp"
    if targ_dir.split("/")[-1].isnumeric():
        simple_dir = targ_dir + "/simple_comb/run0/"
        details = get_details(simple_dir)
        targ, end_targ, dist, m10x, m10y, origx, origy, reached, reached_end, time_first_reached, time_inside_goal, time_outside_goal, estopped = details
        data[targ][prefix + "_end"] = end_targ
        data[targ][prefix + "_dist"] = dist
        data[targ][prefix + "_pathx"] = m10x
        data[targ][prefix + "_pathy"] = m10y
        data[targ][prefix + "_reached"] = reached
        data[targ][prefix + "_reached_end"] = reached_end
        data[targ][prefix + "_time_first_reached"] = time_first_reached
        data[targ][prefix + "_time_inside_goal"] = time_inside_goal
        data[targ][prefix + "_time_outside_goal"] = time_outside_goal
        data[targ][prefix + "_estopped"] = estopped

print(data)

df = pd.DataFrame(data).T.reset_index().rename(columns={"level_0": "x", "level_1": "y"})
df.to_csv("./end_data_new.csv")

