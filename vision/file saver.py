import cv2
import math
import os
from collections import deque


import argparse


def empty(a):
    pass

# Create an object to read
# from camera
import numpy as np

video = cv2.VideoCapture("Resources/test_video.mp4")

cv2.namedWindow("TrackBars")
cv2.resizeWindow("TrackBars", 640, 240)
cv2.createTrackbar("Hue Min", "TrackBars", 113, 179, empty)
cv2.createTrackbar("Hue Max", "TrackBars", 179, 179, empty)
cv2.createTrackbar("Sat Min", "TrackBars", 119, 255, empty)
cv2.createTrackbar("Sat Max", "TrackBars", 255, 255, empty)
cv2.createTrackbar("Val Min", "TrackBars", 116, 255, empty)
cv2.createTrackbar("Val Max", "TrackBars", 255, 255, empty)
ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=16,
                help="max buffer size")
args = vars(ap.parse_args())
pts = deque(maxlen=args["buffer"])
# We need to check if camera
# is opened previously or not

# We need to set resolutions.
# so, convert them from float to integer.
frame_width = int(video.get(3))
frame_height = int(video.get(4))

size = (frame_width, frame_height)

# Below VideoWriter object will create
# a frame of above defined The output
# is stored in 'filename.avi' file.
result = cv2.VideoWriter('videoasdf.avi',
                         cv2.VideoWriter_fourcc(*'MJPG'),
                         10, size)

while (True):
    ret, frame = video.read()
    edges = frame.copy()
    capHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h_min = cv2.getTrackbarPos("Hue Min", "TrackBars")
    h_max = cv2.getTrackbarPos("Hue Max", "TrackBars")
    s_min = cv2.getTrackbarPos("Sat Min", "TrackBars")
    s_max = cv2.getTrackbarPos("Sat Max", "TrackBars")
    v_min = cv2.getTrackbarPos("Val Min", "TrackBars")
    v_max = cv2.getTrackbarPos("Val Max", "TrackBars")
    #print(h_min, h_max, s_min, s_max, v_min, v_max)
    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])
    capHSV = cv2.GaussianBlur(capHSV, (25, 25), 0)
    mask = cv2.inRange(capHSV, lower, upper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    imgResult = cv2.bitwise_and(frame, frame, mask=mask)
    imgCanny = cv2.Canny(mask, 30, 200)
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
        for a in contours:
            M = cv2.moments(a)
            if M['m00'] > 2000:
                ((x, y), radius) = cv2.minEnclosingCircle(a)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 68), 10)
                cv2.circle(frame, center, 2, (255, 0, 255), 10)
                # for deque tracker
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
        centerFinal = (int(averageX / 3), int(averageY / 3))
        cv2.putText(frame, str(centerFinal), (int(averageX / 3) - 85, int(averageY / 3) - 90), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 255, 255), 2)

        # calculation of angle
        changeInX = x2 - x1
        changeInY = y2 - y1
        print(x1, y1)
        print(x2, y2)
        print(changeInX, changeInY)

        ratio = changeInY / changeInX
        angleRadians = math.atan(ratio)
        angleDegrees = math.degrees(angleRadians)
        print(ratio)
        print(angleDegrees)

        cv2.putText(frame, "Angle: " + str(angleDegrees), (int(averageX / 3) - 140, int(averageY / 3) + 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        print("Average of Circle Center Points: " + str(centerFinal))
        pts.appendleft(centerFinal)
        # deque tracker
        # only works if input is video file
    for i in range(1, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        if pts[i - 1] is None or pts[i] is None:
            continue
         # otherwise, compute the thickness of the line and
         # draw the connecting lines
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 10)
        cv2.line(frame, pts[i - 1], pts[i], (255, 0, 255), thickness)
    if ret == True:


        # Write the frame into the
        # file 'filename.avi'
        result.write(frame)

        # Display the frame
        # saved in the file
        cv2.imshow('Frame', frame)

        # Press S on keyboard
        # to stop the process
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break

    # Break the loop
    else:
        break

# When everything done, release
# the video capture and video
# write objects
video.release()
result.release()

# Closes all the frames
cv2.destroyAllWindows()

print("The video was successfully saved")