import cv2
import numpy as np
import os

def empty(a):
    pass

def getDirectory():
    return os.getcwd()

def setDirectory(x):
    os.chdir(x)
    print("Directory Changed to:" + os.getcwd())

def markers(mediaDirectory):

    #trackbar for Red HSV
    cv2.namedWindow("TrackBarsRed")
    cv2.resizeWindow("TrackBarsRed", 640, 240)
    cv2.createTrackbar("Hue Min","TrackBarsRed",0,179,empty)
    cv2.createTrackbar("Hue Max","TrackBarsRed",179,179,empty)
    cv2.createTrackbar("Sat Min","TrackBarsRed",100,255,empty)
    cv2.createTrackbar("Sat Max","TrackBarsRed",255,255,empty)
    cv2.createTrackbar("Val Min","TrackBarsRed",165,255,empty)
    cv2.createTrackbar("Val Max","TrackBarsRed",255,255,empty)

    # trackbar for Blue HSV
    cv2.namedWindow("TrackBarsBlue")
    cv2.resizeWindow("TrackBarsBlue", 640, 240)
    cv2.createTrackbar("Hue Min", "TrackBarsBlue", 81, 179, empty)
    cv2.createTrackbar("Hue Max", "TrackBarsBlue", 124, 179, empty)
    cv2.createTrackbar("Sat Min", "TrackBarsBlue", 110, 255, empty)
    cv2.createTrackbar("Sat Max", "TrackBarsBlue", 231, 255, empty)
    cv2.createTrackbar("Val Min", "TrackBarsBlue", 114, 255, empty)
    cv2.createTrackbar("Val Max", "TrackBarsBlue", 174, 255, empty)




    while True:
        img = cv2.imread(mediaDirectory)
        img = img[0:1920, 500:1300]
        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # update Red trackbar values
        h_minR = cv2.getTrackbarPos("Hue Min", "TrackBarsRed")
        h_maxR = cv2.getTrackbarPos("Hue Max", "TrackBarsRed")
        s_minR = cv2.getTrackbarPos("Sat Min", "TrackBarsRed")
        s_maxR = cv2.getTrackbarPos("Sat Max", "TrackBarsRed")
        v_minR = cv2.getTrackbarPos("Val Min", "TrackBarsRed")
        v_maxR = cv2.getTrackbarPos("Val Max", "TrackBarsRed")
        print(h_minR, h_maxR, s_minR, s_maxR, v_minR, v_maxR)
        lowerRed = np.array([h_minR, s_minR, v_minR])
        upperRed = np.array([h_maxR, s_maxR, v_maxR])

        # update Blue trackbar values
        h_minB = cv2.getTrackbarPos("Hue Min", "TrackBarsBlue")
        h_maxB = cv2.getTrackbarPos("Hue Max", "TrackBarsBlue")
        s_minB = cv2.getTrackbarPos("Sat Min", "TrackBarsBlue")
        s_maxB = cv2.getTrackbarPos("Sat Max", "TrackBarsBlue")
        v_minB = cv2.getTrackbarPos("Val Min", "TrackBarsBlue")
        v_maxB = cv2.getTrackbarPos("Val Max", "TrackBarsBlue")
        print(h_minB, h_maxB, s_minB, s_maxB, v_minB, v_maxB)
        lowerBlue = np.array([h_minB, s_minB, v_minB])
        upperBlue = np.array([h_maxB, s_maxB, v_maxB])

        imgHSV = cv2.GaussianBlur(imgHSV, (25, 25), 0)
        maskRed = cv2.inRange(imgHSV, lowerRed, upperRed)
        maskBlue = cv2.inRange(imgHSV, lowerBlue, upperBlue)
        maskRed = cv2.erode(maskRed, None, iterations=3)
        maskRed = cv2.dilate(maskRed, None, iterations=3)
        maskBlue = cv2.erode(maskBlue, None, iterations=4)
        maskBlue = cv2.dilate(maskBlue, None, iterations=4)
        mask = maskRed | maskBlue
        imgResult = cv2.bitwise_and(img, img, mask=mask)
        originalImage = cv2.resize(img, None, None, 0.4, 0.4, None)
        HSVImage = cv2.resize(imgHSV, None, None, 0.4, 0.4, None)
        resultImage = cv2.resize(imgResult, None, None, 0.6, 0.6, None)
        mask = cv2.resize(mask, None, None, 0.6, 0.6, None)
        cv2.imshow("Original", originalImage)
        cv2.imshow("HSV", HSVImage)
        cv2.imshow("Result", resultImage)
        cv2.imshow("Mask", mask)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

