import cv2

cam = cv2.VideoCapture(-1, cv2.CAP_V4L)

while(True):
    ret, image = cam.read()
    if (ret):
        cv2.imshow("image", image)