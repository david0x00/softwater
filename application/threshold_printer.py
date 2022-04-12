import cv2
import markerdetector
import numpy as np

img = cv2.imread("box_guess.jpg")
blur_img = cv2.GaussianBlur(img, (3,3), 0)
cv2.imwrite("blue.jpg", blur_img)
red_mask = cv2.inRange(blur_img, np.array([0,0,141]), np.array([141,137,255]))
cv2.imwrite("range.jpg", red_mask)
#red_mask = cv2.erode(red_mask, None, iterations=3)
#cv2.imwrite("erode.jpg", red_mask)
#red_mask = cv2.dilate(red_mask, None, iterations=3)
#cv2.imwrite("dilate.jpg", red_mask)

pixel=[29,26]
print(blur_img[pixel[0]][pixel[1]])
blur_img[pixel[0]][pixel[1]] = [0,255,0]
cv2.imwrite("greendot.jpg", blur_img)

#for i in range(32):
    #print(img[32+i][32])
    #print(img[32-i][32])
    #print(img[32][32+i])
#    print(img[32][32-i])


# red_mask = self.get_red_mask(markerGuess, (3,3))