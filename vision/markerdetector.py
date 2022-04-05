import cv2
import math
import numpy as np

mtx = np.array([
    [1535.10668, 0, 954.393136],
    [0, 1530.80529, 543.030187],
    [0,0,1]
])

newcameramtx = np.array([
    [1559.8905, 0, 942.619458],
    [0, 1544.98389, 543.694259],
    [0,0,1]
])

inv_camera_mtx = np.linalg.inv(newcameramtx)

dist = np.array([[0.19210016, -0.4423498, 0.00093771, -0.00542759, 0.25832642 ]])

camera_to_markers_dist = 57.055 #cm

def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))

class MarkerDetector:
    """Handles the conversion of photo to marker values."""

    bounding_box_dim = math.floor(65 / 2)

    def __init__(self, init_img, colorthreshold):
        self.lower = colorthreshold[0]
        self.upper = colorthreshold[1]
        self.init_undistort(init_img)
        self.currentStates = self.analyze_thresh_pix(init_img)
    
    def init_undistort(self, init_img):
        # OLD WAY
        # undistorted_img = cv2.undistort(img, mtx, dist, None, newcameramtx)
        # img = cv2.imread(init_image)
        img = init_img
        h = img.shape[0]
        w = img.shape[1]
        self.mapx, self.mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w,h), cv2.CV_32FC1)

    def get_red_mask(self, image, blur):
        # hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        blur_img = cv2.GaussianBlur(image, blur, 0)
        red_mask = cv2.inRange(blur_img, self.lower, self.upper)
        red_mask = cv2.erode(red_mask, None, iterations=3)
        red_mask = cv2.dilate(red_mask, None, iterations=3)
        return red_mask

    def analyze_thresh(self, img):
        pixel_coords = self.analyze_thresh_pix(img)
        return self.pix2world(pixel_coords)

    # Note: Analyzes images by using basic pixel thresholding method.
    #       Computes marker locations (pixels) and returns.
    def analyze_thresh_pix(self, img):
        # Get image and undistort.
        # img = cv2.imread(img_name)
        undistorted_img = cv2.remap(img, self.mapx, self.mapy, interpolation=cv2.INTER_LINEAR)

        # Mask out all non-red pixels.
        red_mask = self.get_red_mask(undistorted_img, (3, 3))
        cv2.imwrite("test_undistort.jpg", undistorted_img)
        cv2.imwrite("test_masked.jpg", red_mask)

        # Draw circles around clusters of red pixels.
        contours, hierarchy = cv2.findContours(red_mask,
                                               cv2.RETR_EXTERNAL,
                                               cv2.CHAIN_APPROX_SIMPLE)

        # Get relevant circles into a list.
        center_list = []
        for c in contours:
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            #print((x,y))
            if x > 300 and x < 1750:
                if not (x < 410 and y > 1045):
                    center_list.append((x, y))
        
        # Check for error.
        if len(center_list) != 11:
            print("Incorrect Marker Detection...")
            # TODO: Make program run the full sweep if it loses markers
            return None
        
        return center_list

    def analyze_threshold_fast(self, img):
        pixel_coords = self.analyze_threshold_fast_pix(img)
        return self.pix2world(pixel_coords)

    def analyze_threshold_fast_pix(self, img):
        #img = cv2.imread(img_name)
        # undistorted_img = cv2.undistort(img, mtx, dist, None, newcameramtx)
        undistorted_img = cv2.remap(img, self.mapx, self.mapy, interpolation=cv2.INTER_LINEAR)
        imageX, imageY, _ = undistorted_img.shape

        newCenters = []
        for i, marker in enumerate(self.currentStates):
            #print(marker)
            x = math.floor(marker[0])
            y = math.floor(marker[1])
            # crop based on pervious positions [y1:y2, x1:x2] making top left (x1, y1) to bottom right (x2, y2)
            y1 = clamp(0, y - self.bounding_box_dim, imageY)
            y2 = clamp(0, y + self.bounding_box_dim, imageY)
            x1 = clamp(0, x - self.bounding_box_dim, imageX)
            x2 = clamp(0, x + self.bounding_box_dim, imageX)

            markerGuess = undistorted_img[y1:y2, x1:x2]
            # cv2.imwrite("box/box" + str(i) + ".jpg", markerGuess)

            red_mask = self.get_red_mask(markerGuess, (3,3))
            # cv2.imwrite("box/box_mask" + str(i) + ".jpg", red_mask)
            edged = red_mask.copy()
            contours, hierarchy = cv2.findContours(red_mask,
                                            cv2.RETR_EXTERNAL,
                                            cv2.CHAIN_APPROX_SIMPLE)

            if len(contours) > 0:
                circle = cv2.minEnclosingCircle(contours[0])
                self.currentStates[i] = circle[0] + np.array([x - self.bounding_box_dim,y - self.bounding_box_dim])
            #newCenters.append(circle[0] + np.array([x - half_bounding_box_pixel_length,y - half_bounding_box_pixel_length])) # (x,y) position of circle in pixels

        return self.currentStates
        #self.currentStates = newCenters
        #return newCenters


    def pix2world(self, center_list):
        # Convert pixel coordinates to world coordinates.
        center_list.sort(key=lambda x: x[1])
        center_list.reverse()

        center_list_3d = []
        for center in center_list:
            coord_2d = np.array([[center[0]],
                                [center[1]],
                                [1]])
            coord_3d = np.matmul(inv_camera_mtx, coord_2d) * camera_to_markers_dist
            center_list_3d.append((coord_3d[0][0], coord_3d[1][0]))
        
        base_point = center_list_3d[0]
        x_base = base_point[0]
        y_base = base_point[1]

        # Package up data and return.
        row_dict = {}
        for idx in range(11):
            x_key = "M" + str(idx) + "X"
            y_key = "M" + str(idx) + "Y"
            t_key = "M" + str(idx) + "T"

            x_val = center_list_3d[idx][0] - x_base
            y_val = y_base - center_list_3d[idx][1]
            t_val = 0

            row_dict[x_key] = x_val
            row_dict[y_key] = y_val
            row_dict[t_key] = t_val

        return row_dict