import cv2
import numpy as np
import time
from scipy.spatial import distance
from collections import OrderedDict
# import skg

mtx = np.array([
    [1142.77, 0, 920.91],
    [0, 1138.46, 545.01],
    [0, 0, 1]
])

newcameramtx = np.array([
    [1135.68, 0, 919.23],
    [0, 1132.81, 543.06],
    [0, 0, 1]
])

inv_camera_mtx = np.linalg.inv(newcameramtx)

dist = np.array([[ 0.20121649, -0.49210822, -0.00094167, -0.00054018, 0.29212259]])

camera_to_markers_dist = 77.47 #cm

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

    def __repr__(self):
        return f'({self.x}, {self.y})'
        

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

    def update(self, pts, dt: float, sort_y=True):
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
            if sort_y:
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
            else:
                ordered_pts = pts
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
        self.robot_segments = 16
        self.max_pts = self.robot_segments + 2 * (int(self.robot_segments / 5) + 1)
        self.detector = cv2.SimpleBlobDetector_create(self.params)

        self.set_dims(1920, 1080)
    
    def update_params(self):
        self.detector = cv2.SimpleBlobDetector_create(self.params)
    
    def reset(self):
        self.tracker.clear()
    
    def set_dims(self, width, height):
        self.mapx, self.mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (width, height), cv2.CV_32FC1)
    
    def pix2world(self, objects):
        world_objects = []
        for obj_id in objects.keys():
            coord_2d = np.array([[objects[obj_id].x],
                                    [objects[obj_id].y],
                                    [1]])
            coord_3d = np.matmul(inv_camera_mtx, coord_2d) * camera_to_markers_dist
            world_objects.append((coord_3d[0][0], coord_3d[1][0]))
        return world_objects

    def _order(self, pts):
        ordered = []
        for pt in pts:
            if len(ordered) == 0:
                ordered.append(pt)
            else:
                inserted = False
                for i in range(len(ordered)):
                    if pt.x <= ordered[i].x:
                        ordered.insert(i, pt)
                        inserted = True
                if not inserted:
                    ordered.append(pt)
        return ordered

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

        mask = cv2.GaussianBlur(mask, self.gaussian_blur, cv2.BORDER_DEFAULT).astype(np.float32) / 255
        mask = mask ** 0.5
        mask *= 255
        mask = mask.astype(np.uint8)

        keypoints = self.detector.detect(mask)
        pts = []
        for pt in keypoints:
            pts.append(TrackingPoint(pt.pt[0], pt.pt[1], size=pt.size))
        
        if len(self.tracker.objects) == 0:
            if len(pts) == self.max_pts:
                objects = self.tracker.update(pts, dt)
                spine_pts = []
                angle_pts = []
                sp = sorted([objects[0], objects[1], objects[2]], key=lambda pt : pt.x)
                spine_pts.append(sp[1])
                sp.pop(1)
                angle_pts += sp
                i = 3
                while i < self.max_pts:
                    for _ in range(4):
                        spine_pts.append(objects[i])
                        i += 1
                    sp = sorted([objects[i], objects[i + 1], objects[i + 2]], key=lambda pt : pt.x)
                    spine_pts.append(sp[1])
                    sp.pop(1)
                    angle_pts += sp
                    i += 3
                self.tracker.clear()
                self.tracker.update(spine_pts + angle_pts, dt, sort_y=False)
            else:
                objects = dict()
        else:
            objects = self.tracker.update(pts, dt)

        detection = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        
        for i in range(self.max_pts):
            if not i in objects.keys():
                return False, undistorted_img, detection
        
        lines = []
        for i in range(self.robot_segments, self.max_pts, 2):
            lines.append([objects[i], objects[i + 1]])
        
        detection = self.draw_objects(detection, objects)
        undistorted_img = self.draw_lines(undistorted_img, lines, thickness=2)
        undistorted_img = self.draw_objects(undistorted_img, objects)
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
    
    def draw_lines(self, image, lines, color=(255, 0, 255), thickness=1):
        for line in lines:
            x1 = int(line[0].x)
            y1 = int(line[0].y)
            x2 = int(line[1].x)
            y2 = int(line[1].y)
            image = cv2.line(image, (x1, y1), (x2, y2), color, thickness)
        return image


if __name__ == "__main__":
    detector = RobotDetector()
    detector.main_color_hue = 177
    detector.main_color_hue_error = 7
    detector.main_color_low_sat = 65
    detector.main_color_low_val = 80
    detector.gaussian_blur = (3, 3)
    detector.params.minCircularity = 0.0
    detector.params.minArea = 10
    detector.params.minInertiaRatio = 0.2
    detector.update_params()

    img = cv2.imread("./data/test2.jpg")
    img = cv2.resize(img, (1920, 1080))
    detecting, image, track = detector.detect(img)
    image = cv2.resize(image, (960, 720))
    track = cv2.resize(track, (960, 720))
    cv2.imshow('image', image)
    cv2.imshow('track', track)
    cv2.waitKey(0)
