import cv2

img1 = cv2.imread("ud1.jpg")
img2 = cv2.imread("ud2.jpg")

x = 1920
y = 1080

for r in range(y):
    for c in range(x):
        if img1[r][c][0] != img2[r][c][0] or \
           img1[r][c][1] != img2[r][c][1] or \
           img1[r][c][2] != img2[r][c][2]: 
            print("old: " + str(img1[r][c]) + ", new: " + str(img2[r][c]))