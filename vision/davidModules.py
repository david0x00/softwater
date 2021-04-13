import csv
import os
import cv2
import mainvision

csv_headers = ["M1X", "M1Y", "M1T", 
               "M2X", "M2Y", "M2T",
               "M3X", "M3Y", "M3T",
               "M4X", "M4Y", "M4T",
               "M5X", "M5Y", "M5T",
               "M6X", "M6Y", "M6T",
               "M7X", "M7Y", "M7T",
               "M8X", "M8Y", "M8T",
               "M9X", "M9Y", "M9T",
               "M10X", "M10Y", "M10T",
               "M11X", "M11Y", "M11T"]

def writeHeaders(file_name):
    with open(file_name, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=csv_headers)
        writer.writeheader()

def writeRow(file_name, marker_dict):
    with open(file_name, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=csv_headers)
        writer.writerow(marker_dict)

def imageCount(directory):
    img_list = os.listdir(directory)
    for idx, img_name in enumerate(img_list):
        img_list[idx] = int(img_name.split(".")[0])
    return max(img_list)

# The Key function: analyzes images and gets positions and angles
def analyzeImage(img_name):
    img = cv2.imread(img_name)
    cv2.imshow("raw", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# Computer vision marker analyzer
# INPUT: directory with ordered list of photos: 1.jpg, 2.jpg, ...
# OUTPUT: CSV file with the position and angle of all markers.
def analyzeImages(directory):
    file_name = "/".join(directory.split("/")[:-1]) + "/" + directory.split("/")[-1] + "_markers.csv"

    writeHeaders(file_name)

    image_count = imageCount(directory)

    for i in range(image_count):
        img_name = directory + "/" + str(i+1) + ".jpg"

        marker_dict = analyzeImage(img_name)

        writeRow(file_name, marker_dict)

if __name__ == "__main__":
    directory = "/media/user1/Data 2000/soft_robotics_experiments/module_2_single_actuator_right/m2_right_actuator_simple"
    #analyzeImages(directory)
    img_name = directory + "/1.jpg"
    analyzeImage(img_name)

