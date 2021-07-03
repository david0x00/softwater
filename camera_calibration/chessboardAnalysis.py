import numpy as numpy
import cv2
import glob

#termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

d1 = 7
d2 = 10

#prepare object points, like (0,0,0), (1,0,0), etc...
objp = np.zeros((d1*d2,3), np.float32)
objp[:,:2] = np.mgrid[0:d2,0:d1].T.reshape(-1,2)

# arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane

images = glob.glob('*.jpg')

for fname in images:
    #img = cv2.imr
    pass
