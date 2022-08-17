import cv2
import numpy as np
import time
import math
from scipy.spatial import distance_matrix
from centroid_tracker import CentroidTracker, TrackingPoint


class RobotDetector:
    def __init__(self):
        self.main_color_hue = 175
        self.main_color_hue_error = 4
        self.main_color_low_sat = 40
        self.main_color_high_sat = 255
        self.main_color_low_val = 100
        self.main_color_high_val = 230
        self.gaussian_blur = (25, 25)
        self.params = cv2.SimpleBlobDetector_Params()
        self.params.filterByColor = True
        self.params.blobColor = 255
        self.params.filterByCircularity = True
        self.params.minCircularity = 0.4
        self.params.maxCircularity = float('inf')
        self.params.filterByArea = True
        self.params.minArea = 100
        self.params.maxArea = float('inf')
        self.params.filterByInertia = True
        self.params.minInertiaRatio = 0.2
        self.params.maxInertiaRatio = float('inf')
        self.first = True
        self.timestamp = None
        self.tracker = CentroidTracker()
        self.detector = cv2.SimpleBlobDetector_create(self.params)
    
    def update_params(self):
        self.detector = cv2.SimpleBlobDetector_create(self.params)
    
    def detect(self, image, prev_pts=[]):
        if self.first:
            self.timestamp = time.perf_counter()
            self.first = False
        curr = time.perf_counter()
        dt = curr - self.timestamp
        self.timestamp = curr

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        low_hue = self.main_color_hue - self.main_color_hue_error
        high_hue = self.main_color_hue + self.main_color_hue_error

        mask = None

        if (low_hue < 0):
            low_mask = cv2.inRange(hsv, 
            (180 + low_hue, self.main_color_low_sat, self.main_color_low_val), 
            (180, self.main_color_high_sat, self.main_color_high_val))
            high_mask = cv2.inRange(hsv, 
            (0, self.main_color_low_sat, self.main_color_low_val), 
            (high_hue, self.main_color_high_sat, self.main_color_high_val))
            mask = cv2.addWeighted(low_mask, 1, high_mask, 1, 0.0)

        if (high_hue > 180):
            low_mask = cv2.inRange(hsv, 
            (low_hue, self.main_color_low_sat, self.main_color_low_val), 
            (180, self.main_color_high_sat, self.main_color_high_val))
            high_mask = cv2.inRange(hsv, 
            (0, self.main_color_low_sat, self.main_color_low_val), 
            (high_hue - 180, self.main_color_high_sat, self.main_color_high_val))
            mask = cv2.addWeighted(low_mask, 1, high_mask, 1, 0.0)
        
        if mask is None:
            mask = cv2.inRange(hsv, 
            (low_hue, self.main_color_low_sat, self.main_color_low_val), 
            (high_hue, self.main_color_high_sat, self.main_color_high_val))

        mask_blurred = cv2.GaussianBlur(mask, self.gaussian_blur, cv2.BORDER_DEFAULT)

        keypoints = self.detector.detect(mask_blurred)

        pts = []
        for pt in keypoints:
            pts.append(TrackingPoint(pt.pt[0], pt.pt[1], size=pt.size))
        
        show_mask = cv2.cvtColor(mask_blurred, cv2.COLOR_GRAY2BGR)
        

        objects = self.tracker.update(pts, dt)

        detection = self.draw_objects(show_mask, objects)
        

        return pts, detection
    
    def find_indices(self, num, numbers):
        indices = []
        for i in range(len(numbers)):
            if num == numbers[i]:
                indices.append(i)
        return indices

    
    def draw_keypoints(self, image, pts, color=(0, 255, 0)):
        for pt in pts:
            cv2.circle(image, pt.int_xy(), pt.size, color, 2)
        return image
    
    def draw_objects(self, image, objects, color=(0, 255, 0)):
        for obj_id in objects.keys():
            cv2.circle(image, objects[obj_id].int_xy(), int(objects[obj_id].size), color, 2)
        return image


if __name__ == "__main__":
    detector = RobotDetector()

    cap = cv2.VideoCapture("./data/robot_test.mp4")

    detector.main_color_hue = 175
    detector.main_color_hue_error = 5

    pts = []

    start = time.time()
    count = 0
    popped = False
    while True:
        ret, img = cap.read()
        if not ret:
            break

        count = count + 1
        if count < 10:
            continue
        count = 0

        pts, detection = detector.detect(img, pts)

        

        cv2.imshow('detect', detection)
        cv2.waitKey(1)

        

        
