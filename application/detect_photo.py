import markerdetector as md
import cv2
import numpy as np

mint = [0, 0, 141]
#maxt = [141, 137, 255]
maxt = [133, 115, 255]
color_threshold = (np.array(mint), np.array(maxt))

img_file = "/home/pi/Desktop/acc40/38/ampc_comb/run5/imgs/14.jpg"
init_img = cv2.imread(img_file)
cv2.imshow("title",init_img)

mdet = md.MarkerDetector(init_img, color_threshold)