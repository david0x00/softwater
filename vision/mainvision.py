from collections import deque
import cv2
import numpy as np
import argparse
import os
import math
print("Package Imported")


def empty(a):
    pass


def getDirectory():
    return os.getcwd()

def setDirectory(x):
    os.chdir(x)
    print("Directory Changed to:" + os.getcwd())

#setup HSV values for image filtering
#mediaDirectory=0 for webcam or live feed
#otherwise mediaDirectory = path of image or video
def initialHSVsetup(mediaDirectory):
    cap = cv2.VideoCapture(mediaDirectory)



    #trackbar for Red HSV
    cv2.namedWindow("TrackBarsRed")
    cv2.resizeWindow("TrackBarsRed", 640, 240)
    cv2.createTrackbar("Hue Min","TrackBarsRed",0,179,empty)
    cv2.createTrackbar("Hue Max","TrackBarsRed",179,179,empty)
    cv2.createTrackbar("Sat Min","TrackBarsRed",169,255,empty)
    cv2.createTrackbar("Sat Max","TrackBarsRed",248,255,empty)
    cv2.createTrackbar("Val Min","TrackBarsRed",202,255,empty)
    cv2.createTrackbar("Val Max","TrackBarsRed",255,255,empty)

    # trackbar for Blue HSV
    cv2.namedWindow("TrackBarsBlue")
    cv2.resizeWindow("TrackBarsBlue", 640, 240)
    cv2.createTrackbar("Hue Min", "TrackBarsBlue", 111, 179, empty)
    cv2.createTrackbar("Hue Max", "TrackBarsBlue", 136, 179, empty)
    cv2.createTrackbar("Sat Min", "TrackBarsBlue", 103, 255, empty)
    cv2.createTrackbar("Sat Max", "TrackBarsBlue", 255, 255, empty)
    cv2.createTrackbar("Val Min", "TrackBarsBlue", 148, 255, empty)
    cv2.createTrackbar("Val Max", "TrackBarsBlue", 255, 255, empty)

    #deque setup
    #only for video file
    ap = argparse.ArgumentParser()
    ap.add_argument("-b", "--buffer", type=int, default=16,
        help="max buffer size")
    args = vars(ap.parse_args())
    pts = deque(maxlen=args["buffer"])



    #open video file and apply masks
    while True:
        success, img = cap.read()
        capHSV = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

        #update Red trackbar values
        h_minR = cv2.getTrackbarPos("Hue Min","TrackBarsRed")
        h_maxR = cv2.getTrackbarPos("Hue Max","TrackBarsRed")
        s_minR = cv2.getTrackbarPos("Sat Min","TrackBarsRed")
        s_maxR = cv2.getTrackbarPos("Sat Max","TrackBarsRed")
        v_minR = cv2.getTrackbarPos("Val Min","TrackBarsRed")
        v_maxR = cv2.getTrackbarPos("Val Max","TrackBarsRed")
        print(h_minR,h_maxR,s_minR,s_maxR,v_minR,v_maxR)
        lowerRed = np.array([h_minR,s_minR,v_minR])
        upperRed = np.array([h_maxR,s_maxR,v_maxR])

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

        #blur hsv, construct mask, remove artifacts/noise, combine mask with original image
        capHSV = cv2.GaussianBlur(capHSV, (25, 25), 0)
        maskRed = cv2.inRange(capHSV,lowerRed,upperRed)
        maskBlue = cv2.inRange(capHSV, lowerBlue, upperBlue)
        maskRed = cv2.erode(maskRed, None, iterations=2)
        maskRed = cv2.dilate(maskRed, None, iterations=2)
        maskBlue = cv2.erode(maskBlue, None, iterations=2)
        maskBlue = cv2.dilate(maskBlue, None, iterations=2)
        mask = maskRed | maskBlue
        imgResult = cv2.bitwise_and(img,img,mask=mask)






        # Circle Tracking---------------------------------------------

        #determine countours(test between using mask, isolated marker image, and Canny)
        #initialize center of ball - (x,y)
        edged = mask.copy()
        contours, hierarchy = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)



        if len(contours) > 0:
            i = 0
            j = 0
            print("# of Contours Detected = " + str(len(contours)))
            averageX = 0
            averageY = 0
            x1 = 0
            y1 = 0
            x2 = 0
            y2 = 0
            b = max(contours, key=cv2.contourArea)
            G = cv2.moments(b)
            for a in contours:
                M = cv2.moments(a)
                if M['m00'] > (G['m00'] / 2):
                    ((x, y), radius) = cv2.minEnclosingCircle(a)
                    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                    cv2.circle(img, (int(x), int(y)), int(radius), (0,255,68), 10)
                    cv2.circle(img, center, 2, (255, 0, 255), 10)
                    #for deque tracker
                    averageX = averageX + int(M["m10"] / M["m00"])
                    averageY = averageY + int(M["m01"] / M["m00"])
                    if i == 0:
                        x1 = int(M["m10"] / M["m00"])
                        y1 = int(M["m01"] / M["m00"])
                    if i == 2:
                        x2 = int(M["m10"] / M["m00"])
                        y2 = int(M["m01"] / M["m00"])
                    i = i + 1
                if i == 0:
                    print("Contour " + str(j) + " < " + "threshold")
                else:
                    print("Contour " + str(j) + ":" + "passed area threshold")
                j = j + 1
                if i > 3:
                    print("More than 3 contours detected: Edit Mask or HSV settings to eliminate noise/artifacts "
                          "or check if there are more than 3 robot markers.\nBut first, check your threshold value for "
                          "considering a contour.")
            centerFinal = (int(averageX/3), int(averageY/3))
            cv2.putText(img, str(centerFinal), (int(averageX/3) - 85, int(averageY/3) - 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            #calculation of angle
            changeInX = x2 - x1
            changeInY = y2 - y1
            print(x1, y1)
            print(x2, y2)
            print(changeInX, changeInY)

            ratio = changeInY/changeInX
            angleRadians = math.atan(ratio)
            angleDegrees = math.degrees(angleRadians)
            print(ratio)
            print(angleDegrees)

            cv2.putText(img, "Angle: " + str(angleDegrees), (int(averageX / 3) - 140, int(averageY / 3) + 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            print("Average of Circle Center Points: " + str(centerFinal))
            pts.appendleft(centerFinal)





        #deque tracker
        #only works if input is video file
        for i in range(1, len(pts)):
            # if either of the tracked points are None, ignore
            # them
            if pts[i - 1] is None or pts[i] is None:
                continue
            # otherwise, compute the thickness of the line and
            # draw the connecting lines
            thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 10)
            cv2.line(img, pts[i - 1], pts[i], (255, 0, 255), thickness)

        # resize video window based on monitor size
        resizeOne = 0.2
        resizeTwo = 0.2
        isolatedMarkerImg = cv2.resize(imgResult, None, None, resizeOne, resizeOne, None)
        finalImg = cv2.resize(img, None, None, resizeTwo, resizeTwo, None)
        finalHSVImg = cv2.resize(capHSV, None, None, resizeOne, resizeOne, None)
        finalMask = cv2.resize(mask, None, None, resizeOne, resizeOne, None)
        contouredImg = cv2.resize(edged, None, None, resizeOne, resizeOne, None)

        #open video windows
        cv2.imshow("Mask + Original = Isolated Marker",isolatedMarkerImg)
        cv2.imshow("Original", finalImg)
        cv2.imshow("HSV", finalHSVImg)
        #cv2.imshow("Mask", finalMask)
        #cv2.imshow("Canny", one)
        cv2.imshow("Contour Tracked", contouredImg)


        #quit and control video/frame length
        # set waitkey to 0 for individual photo input and anywhere above 20 for video input
        if cv2.waitKey(0) & 0xFF == ord('q'):
            break
