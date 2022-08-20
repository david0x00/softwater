import cv2
import numpy as np
import time
from scipy.spatial import distance
from collections import OrderedDict

mtx = np.array([
    [1535.10668 / 1.5, 0, 954.393136 / 1.5],
    [0, 1530.80529 / 1.5, 543.030187 / 1.5],
    [0,0,1]
])

newcameramtx = np.array([
    [1559.8905 / 1.5, 0, 942.619458 / 1.5],
    [0, 1544.98389 / 1.5, 543.694259 / 1.5],
    [0,0,1]
])

inv_camera_mtx = np.linalg.inv(newcameramtx)

dist = np.array([[0.19210016, -0.4423498, 0.00093771, -0.00542759, 0.25832642 ]])

camera_to_markers_dist = 57.055 #cm

class TrackingPoint:
    x:      float
    y:      float
    vx:     float
    vy:     float
    size:   float
    disappeared: int = 0

    def __init__(self, x, y, vx=0, vy=0, size=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
    
    def model_motion(self, dt, drag=0):
        '''self.x = self.x + self.vx * dt
        self.y = self.y + self.vy * dt
        self.vx *= drag
        self.vy *= drag'''
        pass
    
    def set_pt(self, pt, dt):
        self.vx = (pt.x - self.x) / dt
        self.vy = (pt.y - self.y) / dt
        self.x = pt.x
        self.y = pt.y
        self.size = pt.size
        self.disappeared = pt.disappeared

    def xy(self):
        return [self.x, self.y]
    
    def int_xy(self):
        return [int(self.x), int(self.y)]
        

class RobotTracker():
    nextObjectID:   int = 0
    objects         = OrderedDict()
    maxDisappeared: int
    maxObjects:     int
    
    def __init__(self, maxDisappeared=100, maxObjects=11):
        self.maxDisappeared = maxDisappeared
        self.maxObjects = maxObjects

    def register(self, tracking_point: TrackingPoint):
        self.objects[self.nextObjectID] = tracking_point
        self.nextObjectID += 1

    def deregister(self, objectID: int):
        del self.objects[objectID]
    
    def clear(self):
        ids = []
        for obj_id in self.objects.keys():
            ids.append(obj_id)
        for id in ids:
            self.deregister(id)
        self.nextObjectID = 0

    def update(self, pts, dt: float):
        for obj_id in self.objects.keys():
            self.objects[obj_id].model_motion(dt)
        
        if len(pts) == 0:
            ids = []
            for objectID in self.objects.keys():
                self.objects[objectID].disappeared += 1

                if self.objects[objectID].disappeared > self.maxDisappeared:
                    ids.append(objectID)
                
            for id in ids:
                self.deregister(id)

            return self.objects

        inputCentroids = np.zeros((len(pts), 2), dtype="float")

        for i in range(len(pts)):
            inputCentroids[i] = (pts[i].x, pts[i].y)

        if len(self.objects) == 0:
            ordered_pts = []
            while len(pts) > 0:
                max_y = None
                idx = -1
                for i in range(len(pts)):
                    if idx == -1 or max_y < pts[i].y:
                        idx = i
                        max_y = pts[i].y
                ordered_pts.append(pts[idx])
                pts.pop(idx)
            for i in range(len(ordered_pts)):
                self.register(ordered_pts[i])
        else:
            objectIDs = list(self.objects.keys())
            objectCentroids = np.zeros((len(objectIDs), 2), dtype="float")
            for i in range(len(objectIDs)):
                objectCentroids[i] = self.objects[objectIDs[i]].xy()

            D = distance.cdist(objectCentroids, inputCentroids)
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            usedRows = set()
            usedCols = set()

            for (row, col) in zip(rows, cols):
                if row in usedRows or col in usedCols:
                    continue

                self.objects[objectIDs[row]].set_pt(pts[col], dt)

                usedRows.add(row)
                usedCols.add(col)

            unusedRows = set(range(0, D.shape[0])).difference(usedRows)
            unusedCols = set(range(0, D.shape[1])).difference(usedCols)

            if D.shape[0] >= D.shape[1]:
                for row in unusedRows:
                    objectID = objectIDs[row]
                    self.objects[objectID].disappeared += 1

                    if self.objects[objectID].disappeared > self.maxDisappeared:
                        self.deregister(objectID)
            else:
                for col in unusedCols:
                    self.register(pts[col])

        return self.objects


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
        self.tracker = RobotTracker()
        self.robot_segments = 11
        self.detector = cv2.SimpleBlobDetector_create(self.params)

        self.init_undistort()
    
    def update_params(self):
        self.detector = cv2.SimpleBlobDetector_create(self.params)
    
    def reset(self):
        self.tracker.clear()

    def init_undistort(self):
        h = 720
        w = 1280
        self.mapx, self.mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w,h), cv2.CV_32FC1)
    
    def pix2world(self, objects):
        world_objects = []
        for obj_id in objects.keys():
            coord_2d = np.array([[objects[obj_id].x],
                                    [objects[obj_id].y],
                                    [1]])
            coord_3d = np.matmul(inv_camera_mtx, coord_2d) * camera_to_markers_dist
            world_objects.append((coord_3d[0][0], coord_3d[1][0]))
        return world_objects

    def detect(self, image):
        undistorted_img = cv2.remap(image, self.mapx, self.mapy, interpolation=cv2.INTER_LINEAR)

        if self.first:
            self.timestamp = time.perf_counter()
            self.first = False
        curr = time.perf_counter()
        dt = curr - self.timestamp
        self.timestamp = curr

        hsv = cv2.cvtColor(undistorted_img, cv2.COLOR_BGR2HSV)

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
        
        check = False
        if len(self.tracker.objects) == 0:
            check = True
        objects = self.tracker.update(pts, dt)

        if (check):
            if len(objects) != self.robot_segments:
                self.tracker.clear()
        
        show_mask = cv2.cvtColor(mask_blurred, cv2.COLOR_GRAY2BGR)
        detection = self.draw_objects(show_mask, objects)

        ids = self.tracker.objects.keys()
        for i in range(self.robot_segments):
            if not i in ids:
                return False, undistorted_img, detection

        return True, undistorted_img, detection
    
    def draw_keypoints(self, image, pts, color=(0, 255, 0)):
        for pt in pts:
            cv2.circle(image, pt.int_xy(), pt.size, color, 2)
        return image
    
    def draw_objects(self, image, objects, color=(0, 255, 0)):
        for obj_id in objects.keys():
            xy = objects[obj_id].int_xy()
            radius = int(objects[obj_id].size / 2)
            cv2.circle(image, xy, radius, color, 2)
            id = str(obj_id)
            size, _ = cv2.getTextSize(id, cv2.FONT_HERSHEY_SIMPLEX, 1, 1)
            xy[0] += int(size[0] / 2)
            xy[1] -= (radius + int(size[1] / 2))
            cv2.putText(image, str(obj_id), xy, cv2.FONT_HERSHEY_SIMPLEX, 1, color, 1, cv2.LINE_AA)
        return image


if __name__ == "__main__":
    detector = RobotDetector()

    cap = cv2.VideoCapture("./data/robot_test.mp4")

    detector.main_color_hue = 174
    detector.main_color_hue_error = 6

    start = time.time()
    count = 0
    changed = False
    while True:
        ret, img = cap.read()
        if not ret:
            break

        count = count + 1
        if count < 10:
           continue
        count = 0

        pts, detection = detector.detect(img)

        if not changed and time.time() - start > 2:
            detector.main_color_hue = 172
            changed = True

        cv2.imshow('detect', detection)
        cv2.waitKey(1)
        time.sleep(0.5)
