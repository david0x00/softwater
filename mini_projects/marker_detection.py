#from msilib.schema import Class
import cv2
import numpy as np
import datetime
import math

# NOTE: Camera Properties for Undistortion
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

roi = (4, 11, 1907, 1059)

camera_to_markers_dist = 57.055 #cm

half_bounding_box_pixel_length = math.floor(65 / 2)


# TODO: Get marker positions using colvolution.
#       Need to create a good "kernel" when is basically
#       what one red marker looks like.
def analyze_image_convolution(img_name):
    pass

# TODO: get marker positions by first getting the bottom marker
#       then taking a guess at where the next one will be and 
#       searching that space, and so on.
def analyze_image_localized_guess(img_name):
    pass

def get_time():
    return datetime.datetime.now()

def clamp(minimum, x, maximum):
        return max(minimum, min(x, maximum))

def print_time_diff(start, end):
    print((end - start).total_seconds())


# Init
# original image that describes original state
# red mask tuned parameters line 38

# Image method computes the new positions of the markers.
# Set bounding box to have sidelength of the length of the blue pixels and fix clipping


# colorthreshold is a tuple (lower, upper)
class MarkerDetector:
    def __init__(self, init_image, colorthreshold):
        self.lower = colorthreshold[0]
        self.upper = colorthreshold[1]
        self.currentStates = self.analyze_image_threshold_pixel_coords_sweeping(init_image)

    # NOTE: This function takes and image and filters for red
    #       dots in the image. Below are threshold settings that have
    #       worked for previous experiments.
    # --------------------------------------------------------
    # This setting worked for module_2_single_actuator_right
    # lower = np.array([120,97,148])
    # upper = np.array([255,255,255])
    # This worked for module1_fullext1
    # lower = np.array([43,61,158])
    # upper = np.array([255,255,255])
    def get_red_mask(self, image):
        #lower = np.array([43,61,159])
        #upper = np.array([255,255,255])
        hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        blur_img = cv2.GaussianBlur(hsv_img, (25,25), 0)
        red_mask = cv2.inRange(blur_img, self.lower, self.upper)
        red_mask = cv2.erode(red_mask, None, iterations=3)
        red_mask = cv2.dilate(red_mask, None, iterations=3)
        return red_mask

    # Must be fed consequtive images
    def analyze_image_threshold_fast(self, img_name):
        pixelCoords = self.analyze_image_threshold_pixel_coords_fast(img_name)
        return self.convertPixeltoWorldCoordinates(pixelCoords)

    def analyze_image_threshold_pixel_coords_fast(self, img_name):
        img = cv2.imread(img_name)
        undistorted_img = cv2.undistort(img, mtx, dist, None, newcameramtx)
        imageX, imageY, _ = undistorted_img.shape

        newCenters = []
        for marker in self.currentStates:
            x = math.floor(marker[0])
            y = math.floor(marker[1])
            # crop based on pervious positions [y1:y2, x1:x2] making top left (x1, y1) to bottom right (x2, y2)
            y1 = clamp(0, y - half_bounding_box_pixel_length, imageY)
            y2 = clamp(0, y + half_bounding_box_pixel_length, imageY)
            x1 = clamp(0, x - half_bounding_box_pixel_length, imageX)
            x2 = clamp(0, x + half_bounding_box_pixel_length, imageX)

            markerGuess = undistorted_img[y1:y2, x1:x2]
            #cv2.imwrite("test.jpg", markerGuess)

            red_mask = self.get_red_mask(markerGuess)
            edged = red_mask.copy()
            contours, hierarchy = cv2.findContours(red_mask,
                                            cv2.RETR_EXTERNAL,
                                            cv2.CHAIN_APPROX_SIMPLE)

            circle = cv2.minEnclosingCircle(contours[0])
            newCenters.append(circle[0] + np.array([x - half_bounding_box_pixel_length,y - half_bounding_box_pixel_length])) # (x,y) position of circle in pixels
        
        self.currentStates = newCenters
        return newCenters

    # Note: Analyzes images by using basic pixel thresholding method.
    #       Then, it computes marker locations (cm) and returns.
    def analyze_image_threshold_sweeping(self, img_name):
        pixelCoords = self.analyze_image_threshold_pixel_coords_sweeping(img_name)
        return self.convertPixeltoWorldCoordinates(pixelCoords)

    # Note: Analyzes images by using basic pixel thresholding method.
    #       Computes marker locations (pixels) and returns.
    def analyze_image_threshold_pixel_coords_sweeping(self, img_name):
        # Get image and undistort.
        img = cv2.imread(img_name)
        undistorted_img = cv2.undistort(img, mtx, dist, None, newcameramtx)

        # Mask out all non-red pixels.
        red_mask = self.get_red_mask(undistorted_img)
        #cv2.imwrite("40_masked.jpg", red_mask)

        # Draw circles around clusters of red pixels.
        edged = red_mask.copy()
        contours, hierarchy = cv2.findContours(red_mask,
                                            cv2.RETR_EXTERNAL,
                                            cv2.CHAIN_APPROX_SIMPLE)

        # Get relevant circles into a list.
        center_list = []
        for c in contours:
            ((x,y), radius) = cv2.minEnclosingCircle(c)
            if x > 300 and x < 1750:
                center_list.append((x,y))
        
        # Check for error.
        if len(center_list) != 11:
            print("Incorrect Marker Detection...")
            # TODO: Make program run the full sweep if it loses markers
            return
        
        return center_list

    def convertPixeltoWorldCoordinates(self, center_list):
        # Convert pixel coordinates to world coordinates.
        center_list.sort(key = lambda x: x[1])
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

if __name__ == "__main__":
    colorthreshold = (np.array([43,61,159]), np.array([255,255,255]))
    detector = MarkerDetector("mini_projects/imgs/42.jpg", colorthreshold)
    runs = 100
    start_threshold = get_time()
    for i in range(runs):
        marker_locations1 = detector.analyze_image_threshold_pixel_coords_sweeping("mini_projects/imgs/42.jpg")
    end_threshold = get_time()
    print_time_diff(start_threshold, end_threshold)
    start_threshold = get_time()
    for i in range(runs):
        marker_locations2 = detector.analyze_image_threshold_pixel_coords_fast("mini_projects/imgs/42.jpg")
    end_threshold = get_time()
    print_time_diff(start_threshold, end_threshold)
    #print(str(marker_locations1) + "\n")
    #print(marker_locations2)