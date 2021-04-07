import cv2
import numpy as np

def empty(a):
    pass

path = 'Resources/Image from iOS.jpg'
cv2.namedWindow("TrackBars")
cv2.resizeWindow("TrackBars", 640, 240)
cv2.createTrackbar("Hue Min","TrackBars",0,179,empty)
cv2.createTrackbar("Hue Max","TrackBars",179,179,empty)
cv2.createTrackbar("Sat Min","TrackBars",0,255,empty)
cv2.createTrackbar("Sat Max","TrackBars",255,255,empty)
cv2.createTrackbar("Val Min","TrackBars",0,255,empty)
cv2.createTrackbar("Val Max","TrackBars",255,255,empty)

while True:
    img = cv2.imread(path)
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    h_min = cv2.getTrackbarPos("Hue Min","TrackBars")
    h_max = cv2.getTrackbarPos("Hue Max","TrackBars")
    s_min = cv2.getTrackbarPos("Sat Min","TrackBars")
    s_max = cv2.getTrackbarPos("Sat Max","TrackBars")
    v_min = cv2.getTrackbarPos("Val Min","TrackBars")
    v_max = cv2.getTrackbarPos("Val Max","TrackBars")
    print(h_min,h_max,s_min,s_max,v_min,v_max)
    lower = np.array([h_min,s_min,v_min])
    upper = np.array([h_max,s_max,v_max])

    imgHSV = cv2.GaussianBlur(imgHSV, (25, 25), 0)
    mask = cv2.inRange(imgHSV, lower, upper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    imgResult = cv2.bitwise_and(img, img, mask=mask)
    originalImage = cv2.resize(img, None, None, 0.2, 0.2, None)
    HSVImage = cv2.resize(imgHSV, None, None, 0.2, 0.2, None)
    resultImage = cv2.resize(imgResult, None, None, 0.2, 0.2, None)
    cv2.imshow("Original", originalImage)
    cv2.imshow("HSV", HSVImage)
    cv2.imshow("Result", resultImage)
    cv2.waitKey(1)