import cv2
import numpy as np
import datetime

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
def get_red_mask(image):
    lower = np.array([43,61,159])
    upper = np.array([255,255,255])
    hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    blur_img = cv2.GaussianBlur(hsv_img, (25,25), 0)
    red_mask = cv2.inRange(blur_img, lower, upper)
    red_mask = cv2.erode(red_mask, None, iterations=3)
    red_mask = cv2.dilate(red_mask, None, iterations=3)
    return red_mask

# Note: Analyzes images by using basic pixel thresholding method.
#       Then, it computes marker locations (cm) and returns.
def analyze_image_threshold(img_name):
    # Get image and undistort.
    img = cv2.imread(img_name)
    undistorted_img = cv2.undistort(img, mtx, dist, None, newcameramtx)

    # Mask out all non-red pixels.
    red_mask = get_red_mask(undistorted_img)
    cv2.imwrite("40_masked.jpg", red_mask)

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
        return

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

def print_time_diff(start, end):
    print((end - start).total_seconds())

if __name__ == "__main__":
    start_threshold = get_time()
    marker_locations = analyze_image_threshold("40.jpg")
    end_threshold = get_time()
    print_time_diff(start_threshold, end_threshold)


