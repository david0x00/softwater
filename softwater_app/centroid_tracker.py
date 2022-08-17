from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np

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
    
    def model_motion(self, dt):
        self.x = self.x + self.vx * dt
        self.y = self.y + self.vy * dt
    
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
        

class CentroidTracker():
    nextObjectID:   int = 0
    objects:        OrderedDict[TrackingPoint] = OrderedDict()
    maxDisappeared: int
    
    def __init__(self, maxDisappeared=2):
        self.maxDisappeared = maxDisappeared

    def register(self, tracking_point: TrackingPoint):
        self.objects[self.nextObjectID] = tracking_point
        self.nextObjectID += 1

    def deregister(self, objectID: int):
        del self.objects[objectID]

    def update(self, pts: list[TrackingPoint], dt: float):
        for obj_id in self.objects.keys():
            self.objects[obj_id].model_motion(dt)
        
        if len(pts) == 0:
            for objectID in self.objects.keys():
                self.objects[objectID].disappeared += 1

                if self.objects[objectID].disappeared > self.maxDisappeared:
                    self.deregister(objectID)

            return self.objects

        inputCentroids = np.zeros((len(pts), 2), dtype="float")

        for i in range(len(pts)):
            inputCentroids[i] = (pts[i].x, pts[i].y)

        if len(self.objects) == 0:
            for i in range(len(pts)):
                self.register(pts[i])
        else:
            objectIDs = list(self.objects.keys())
            objectCentroids = np.zeros((len(objectIDs), 2), dtype="float")
            for i in range(len(objectIDs)):
                objectCentroids[i] = self.objects[objectIDs[i]].xy()

            D = dist.cdist(objectCentroids, inputCentroids)
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