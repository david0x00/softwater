import cv2
import markerdetector

img = cv2.imread("box_guess.jpg")

for i in range(5):
    print(img[32+i][32])
    print(img[32-i][32])
    print(img[32][32+i])
    print(img[32][32-i])


# red_mask = self.get_red_mask(markerGuess, (3,3))