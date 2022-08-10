from pickletools import uint8
import cv2
import numpy as np
import time

#input_image_path = "./data/test5.jpg"

cam = cv2.VideoCapture("./data/robot_test.mp4")

class RobotDetector:
    def __init__(self):
        self.dims = (1280, 720)
        self.main_color_hue = 169
        self.main_color_hue_error = 3
        self.main_color_low_sat = 40
        self.main_color_high_sat = 255
        self.main_color_low_val = 100
        self.main_color_high_val = 230
        self.gaussian_blur = (25, 25)
        params = cv2.SimpleBlobDetector_Params()
        params.filterByColor = True
        params.blobColor = 255
        params.filterByCircularity = True
        params.minCircularity = 0.6
        params.maxCircularity = float('inf')
        params.filterByArea = True
        params.minArea = 100
        params.filterByInertia = True
        params.minInertiaRatio = 0.2
        params.maxInertiaRatio = float('inf')
        self.detector = cv2.SimpleBlobDetector_create(params)
    
    def detect(self, image):
        img = cv2.resize(image, self.dims, cv2.INTER_AREA)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

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

        cv2.imshow("img2", mask_blurred)
        cv2.waitKey(1)

        keypoints = self.detector.detect(mask_blurred)
        #print(keypoints)
        return keypoints


if __name__ == "__main__":
    from datalink import DataLink

    link = DataLink("Link1", False, "169.254.11.63")
    detector = RobotDetector()

    while True:
        link.update()
        if link.data_available():
            start = time.time()
            msg = link.get()
            img = msg["data"]["image"]
            keypoints = detector.detect(img)
            blank = np.zeros((1, 1))
            
            img = cv2.drawKeypoints(img, keypoints, blank, (0, 255, 0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
            
            img = cv2.resize(img, (1280, 720))
            cv2.imshow("img", img)
            cv2.waitKey(1)
        #print(link.latency(True))

        
