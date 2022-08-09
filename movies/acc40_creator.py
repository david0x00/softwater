import cv2
import numpy as np
import glob
import pandas as pd
from sklearn.metrics import mean_squared_error
from matplotlib import pyplot as plt, patches
import numpy as np

directory = "/Volumes/Flash/acc40/"

def get_end_rmse(directory):
    for filename in glob.glob(directory + "*.csv"):
        data_arr = filename.split("/")[-1].split(".")[0].split("_")
        targ = [float(data_arr[-2]), float(data_arr[-1])]
        df = pd.read_csv(filename)
        end_targ = [round(df["M10X"].iloc[-1], 3), round(df["M10Y"].iloc[-1], 3)]
        rms = round(mean_squared_error(targ, end_targ, squared=False),3)
        print("Goal: " + str(targ) + ", Actual: " + str(end_targ) + ", RMSE: " + str(rms) + " cm")

        return targ, end_targ, rms


if __name__ == "__main__":
    img_array = []

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for targ_dir in glob.glob(directory + "/*"):
        print(targ_dir)
        if targ_dir != "/Volumes/Flash/acc40/controllers" or targ_dir != "/Volumes/Flash/acc40/movies":
            #movie_string = "Target"
            print(targ_dir)
            ampc_dir = targ_dir + "/ampc_comb/run0/"
            simple_dir = targ_dir + "/simple_comb/run0/"
            print("AMPC Controller")
            targ_ampc, end_targ_ampc, rms_ampc = get_end_rmse(ampc_dir)
            print("Simple Controller")
            targ_simp, end_targ_simp, rms_simp = get_end_rmse(simple_dir)
            rect_ampc = patches.Rectangle((end_targ_ampc[0],end_targ_ampc[1]), 2,2,facecolor="green")
            rect_simp = patches.Rectangle((end_targ_simp[0],end_targ_simp[1]), 2,2,facecolor="green")
            ax.add_patch(rect_ampc)
            ax.add_patch(rect_simp)
        plt.show()

    #proj_directory = directory + proj_name
    #for filename in glob.glob(proj_directory + '/*.jpg'):
    #    img = cv2.imread(filename)
    #    height, width, layers = img.shape
    #    size = (width,height)
    #    img_array.append(img)

    #file_name = directory + proj_name + ".mp4"
    #fps = 2
    #mp4_codec = cv2.VideoWriter_fourcc(*'X264')
    #avi_codec = cv2.VideoWriter_fourcc(*'DIVX')
    #out = cv2.VideoWriter(file_name, mp4_codec, fps, size)

    #for i in range(len(img_array)):
    #    out.write(img_array[i])
    
    #out.release()

#coord_3d = np.matmul(inv_camera_mtx, coord_2d) * camera_to_markers_dist