import cv2
import numpy as np

class RobotDetector:
    def __init__(self):
        self.dims = (1280, 720)
        self.main_color_hue = 168
        self.main_color_hue_error = 2
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

        keypoints = self.detector.detect(mask_blurred)
        detection = cv2.drawKeypoints(mask_blurred, keypoints, np.zeros((1, 1)), (0, 255, 0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        return keypoints, detection


if __name__ == "__main__":
    from datalink import DataLink
    from rate import Rate
    import time

    link = DataLink("Link1", False, "169.254.11.63")
    detector = RobotDetector()

    start = time.time()

    main_rate = Rate(200)
    ask_rate = Rate(30)

    back = True

    link.send({'command': 'get keyframe'})

    while True:
        link.update()

        if link.data_available():
            msg = link.get()['data']
            if 'keyframe' in msg.keys():
                link.send({'command': 'get keyframe'})
                print((time.time() - start) * 1000)
                start = time.time()
                img, values = msg['keyframe']
                keypoints, _ = detector.detect(img)
                blank = np.zeros((1, 1))
                
                img = cv2.drawKeypoints(img, keypoints, blank, (0, 255, 0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
                
                img = cv2.resize(img, (1280, 720))
                cv2.imshow("img", img)
                cv2.waitKey(1)
                
        
        main_rate.sleep()
        

        
