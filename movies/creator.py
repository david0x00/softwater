import cv2
import numpy as np
import glob

directory = "/Volumes/Flash/autompc_data/"
proj_name = "random"

if __name__ == "__main__":
    img_array = []

    proj_directory = directory + proj_name
    for filename in glob.glob(proj_directory + '/*.jpg'):
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width,height)
        img_array.append(img)

    file_name = directory + proj_name + ".mp4"
    fps = 2
    mp4_codec = cv2.VideoWriter_fourcc(*'X264')
    avi_codec = cv2.VideoWriter_fourcc(*'DIVX')
    out = cv2.VideoWriter(file_name, mp4_codec, fps, size)

    for i in range(len(img_array)):
        out.write(img_array[i])
    
    out.release()