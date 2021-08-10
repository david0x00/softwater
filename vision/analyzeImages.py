import csv
import os
import cv2
from numpy.lib.polynomial import poly
import mainvision
import numpy as np

csv_headers = ["M0X", "M0Y", "M0T", 
               "M1X", "M1Y", "M1T", 
               "M2X", "M2Y", "M2T",
               "M3X", "M3Y", "M3T",
               "M4X", "M4Y", "M4T",
               "M5X", "M5Y", "M5T",
               "M6X", "M6Y", "M6T",
               "M7X", "M7Y", "M7T",
               "M8X", "M8Y", "M8T",
               "M9X", "M9Y", "M9T",
               "M10X", "M10Y", "M10T"]

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

poly_order = 5

def writeHeaders(file_name, fieldnames):
    with open(file_name, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

def writeRow(file_name, row_dict, fieldnames):
    with open(file_name, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(row_dict)

def imageCount(directory):
    img_list = os.listdir(directory)
    return len(img_list)
    # for idx, img_name in enumerate(img_list):
    #     img_list[idx] = int(img_name.split(".")[0])
    # return max(img_list)

def showImage(title, img):
    cv2.imshow(title, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# This setting worked for module_2_single_actuator_right
# lower = np.array([120,97,148])
# upper = np.array([255,255,255])
# This worked for module1_fullext1
# lower = np.array([43,61,158])
# upper = np.array([255,255,255])
def getRedMask(image):
    lower = np.array([43,61,159])
    upper = np.array([255,255,255])
    hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    blur_img = cv2.GaussianBlur(hsv_img, (25,25), 0)
    red_mask = cv2.inRange(blur_img, lower, upper)
    red_mask = cv2.erode(red_mask, None, iterations=3)
    red_mask = cv2.dilate(red_mask, None, iterations=3)
    return red_mask

# The Key function: analyzes images and gets positions and angles
def analyzeImage(img_name):
    error_detected = False
    img = cv2.imread(img_name)
    undistorted_img = cv2.undistort(img, mtx, dist, None, newcameramtx)

    red_mask = getRedMask(undistorted_img)

    edged = red_mask.copy()
    contours, hierarchy = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    num_of_points = len(contours)

    if num_of_points != 11:
        #print("Error detected initially.")
        #print(img_name)
        #print(num_of_points)
        error_detected = True

    center_list = []
    for c in contours:
        ((x,y), radius) = cv2.minEnclosingCircle(c)
        if x > 300 and x < 1750:
            center_list.append((x,y))
        
    center_list.sort(key = lambda x: x[1])
    center_list.reverse()

    if len(center_list) != 11:
        print("Error still detected.")
        print(img_name)
        print(num_of_points)
        error_detected = True
    elif len(center_list) == 11 and error_detected == True:
        #print("error corrected")
        error_detected = False

    #if error_detected:
    #    return {}
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

    row_dict = {}
    for idx in range(11):
        x_key = "M" + str(idx) + "X"
        y_key = "M" + str(idx) + "Y"
        t_key = "M" + str(idx) + "T"

        if error_detected:
            x_val = 0
            y_val = 0
            t_val = 0
        else:
            x_val = center_list_3d[idx][0] - x_base
            y_val = y_base - center_list_3d[idx][1]
            t_val = 0

        row_dict[x_key] = x_val
        row_dict[y_key] = y_val
        row_dict[t_key] = t_val

    return row_dict


    #print("Contours Detected: " + str(len(contours)))

    #max_contour = max(contours, key=cv2.contourArea)
    #max_moments = cv2.moments(max_contour)

    # Here is the part where we show the circles on the centers.
    # for c in contours:
    #     m = cv2.moments(c)
    #     if m['m00'] > (max_moments['m00']/8):
    #         ((x,y), radius) = cv2.minEnclosingCircle(c)
    #         center = (int(m['m10'] / m['m00']), int(m['m01'] / m['m00']))
    #         #cv2.circle(img, (int(x), int(y)), int(radius), (0,255,68), 10)
    #         cv2.circle(img, center, 2, (255,0,255), 10)


def leastSquaresPolynomial(x, y, order):
    n = len(x)
    M = np.zeros((order+1, order+1))
    b = np.zeros((order+1, 1))
    #build up the M matrix
    M[0][0] = n
    for k in range(1,(2*order)+1):
        #print("break")
        total = 0
        for i in range(n):
            total += x[i]**k
        r = 0
        c = k
        while r <= k and c >= 0:
            #print(str(r) + ", " + str(c))
            if r <= order and r >= 0 and c <= order and c >=0:
                M[r][c] = total
            r += 1
            c -= 1
    
    #build the b matrix
    for k in range(order+1):
        total = 0
        for i in range(n):
            total += y[i] * (x[i]**k)
        b[k][0] = total
    
    a = []
    det_M = np.linalg.det(M)
    
    for k in range(0, order+1):
        Mi = M.copy()
        Mi[:, k] = b[:, 0]
        det_Mi = np.linalg.det(Mi)
        a_k = det_Mi / det_M
        a.append(a_k)
    # a.reverse()
    return a

def calculatePoly(marker_dict):
    x = []
    y = []
    for i in range(11):
        # Switch the X and Y.
        x.append(marker_dict["M" + str(i) + "X"])
        y.append(marker_dict["M" + str(i) + "Y"])
    a = leastSquaresPolynomial(y, x, poly_order)

    poly_dict = {}
    for i in range(poly_order + 1):
        poly_dict["a" + str(i)] = a[i]
    poly_dict["d"] = y[-1]
    
    return poly_dict



# Computer vision marker analyzer
# INPUT: directory with ordered list of photos: 1.jpg, 2.jpg, ...
# OUTPUT: CSV file with the position and angle of all markers.
def analyzeImages(directory):
    marker_file_name = "/".join(directory.split("/")[:-1]) + "/" + directory.split("/")[-1] + "_markers.csv"
    poly_file_name = "/".join(directory.split("/")[:-1]) + "/" + directory.split("/")[-1] + "_poly.csv"
    if os.path.exists(marker_file_name):
        os.remove(marker_file_name)
    if os.path.exists(poly_file_name):
        os.remove(poly_file_name)

    poly_headers = []
    for i in range(poly_order+1):
        poly_headers.append("a" + str(i))
    poly_headers.append("d")
    print(poly_headers)

    writeHeaders(marker_file_name, csv_headers)
    writeHeaders(poly_file_name, poly_headers)

    image_count = imageCount(directory)

    print(image_count)

    for i in range(image_count):
        img_name = directory + "/" + str(i) + ".jpg"

        marker_dict = analyzeImage(img_name)
        poly_dict = calculatePoly(marker_dict)

        writeRow(marker_file_name, marker_dict, csv_headers)
        writeRow(poly_file_name, poly_dict, poly_headers)

if __name__ == "__main__":
    #directory = "/media/user1/Data 2000/soft_robotics_experiments/module_2_single_actuator_right/m2_right_actuator_simple3"
    # directory = "/media/user1/Data 2000/soft_robotics_experiments/training_data/round_1/module2_fullext4"
    directory = "/media/user1/Data 2000/soft_robotics_experiments/training_data/round_1/s_curve2"
    analyzeImages(directory)
    #img_name = directory + "/1.jpg"
    #analyzeImage(img_name)

