from collections import deque
import cv2
import numpy as np
import argparse
import os
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

    #trackbar for HSV
    cv2.namedWindow("TrackBars")
    cv2.resizeWindow("TrackBars", 640, 240)
    cv2.createTrackbar("Hue Min","TrackBars",113,179,empty)
    cv2.createTrackbar("Hue Max","TrackBars",179,179,empty)
    cv2.createTrackbar("Sat Min","TrackBars",119,255,empty)
    cv2.createTrackbar("Sat Max","TrackBars",255,255,empty)
    cv2.createTrackbar("Val Min","TrackBars",116,255,empty)
    cv2.createTrackbar("Val Max","TrackBars",255,255,empty)

    #deque setup
    #only for video files
    ap = argparse.ArgumentParser()
    ap.add_argument("-b", "--buffer", type=int, default=16,
        help="max buffer size")
    args = vars(ap.parse_args())
    pts = deque(maxlen=args["buffer"])

    #open video file and apply masks
    while True:
        success, img = cap.read()
        capHSV = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

        #update trackbar values
        h_min = cv2.getTrackbarPos("Hue Min","TrackBars")
        h_max = cv2.getTrackbarPos("Hue Max","TrackBars")
        s_min = cv2.getTrackbarPos("Sat Min","TrackBars")
        s_max = cv2.getTrackbarPos("Sat Max","TrackBars")
        v_min = cv2.getTrackbarPos("Val Min","TrackBars")
        v_max = cv2.getTrackbarPos("Val Max","TrackBars")
        # print(h_min,h_max,s_min,s_max,v_min,v_max)
        lower = np.array([h_min,s_min,v_min])
        upper = np.array([h_max,s_max,v_max])

        #blur hsv, construct mask, remove artifacts/noise, combine mask with original image
        capHSV = cv2.GaussianBlur(capHSV, (25, 25), 0)
        mask = cv2.inRange(capHSV,lower,upper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        imgResult = cv2.bitwise_and(img,img,mask=mask)
        imgCanny = cv2.Canny(mask, 30, 200)




        # Circle Tracking---------------------------------------------

        #determine countours(test between using mask, isolated marker image, and Canny)
        #initialize center of ball - (x,y)
        edged = mask.copy()
        contours, hierarchy = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        center = None


        if len(contours) > 0:
            i = 0
            j = 0
            print("# of Contours Detected = " + str(len(contours)))
            averageOne = 0
            averageTwo = 0
            for a in contours:
                M = cv2.moments(a)
                if M['m00'] > 4000:
                    ((x, y), radius) = cv2.minEnclosingCircle(a)
                    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                    cv2.circle(img, (int(x), int(y)), int(radius), (0,255,68), 10)
                    cv2.circle(img, center, 2, (255, 0, 255), 10)
                    #for deque tracker
                    averageOne = averageOne + int(M["m10"] / M["m00"])
                    averageTwo = averageTwo + int(M["m01"] / M["m00"])
                    i = i + 1
                if i == 0:
                    print("Contour " + str(j) + " < " + "threshold")
                else:
                    print("Contour " + str(j) + ":" + "passed area threshold")
                j = j + 1
                if i > 3:
                    print("More than 3 contours detected: Edit Mask or HSV settings to eliminate noise/artifacts "
                          "or check if there are more than 3 robot markers.\nBut first check your threshold value for "
                          "considering a contour.")
            centerFinal = (int(averageOne/3), int(averageTwo/3))
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
        isolatedMarkerImg = cv2.resize(imgResult, None, None, 0.3, 0.3, None)
        finalImg = cv2.resize(img, None, None, 0.3, 0.3, None)
        finalHSVImg = cv2.resize(capHSV, None, None, 0.3, 0.3, None)
        finalMask = cv2.resize(mask, None, None, 0.3, 0.3, None)
        contouredImg = cv2.resize(edged, None, None, 0.3, 0.3, None)

        #open video windows
        cv2.imshow("Mask + Original = Isolated Marker",isolatedMarkerImg)
        cv2.imshow("Original", finalImg)
        cv2.imshow("HSV", finalHSVImg)
        #cv2.imshow("Mask", finalMask)
        #cv2.imshow("Canny", one)
        cv2.imshow("Contour Tracked", contouredImg)



        #quit and control video length
        if cv2.waitKey(0) & 0xFF == ord('q'):
            break