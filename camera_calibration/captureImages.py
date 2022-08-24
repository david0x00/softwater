#from picamera import PiCamera
import time
from unicodedata import name
import cv2

#camera = PiCamera(sensor_mode=5, framerate=30)
#camera.start_preview()

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
last = time.time()
i = 0

if __name__ == '__main__':
    directory = "./calibration_images/"
    while True:
        ret, img = cap.read()
        if ret:
            if time.time() >= last + 4:
                file_name = directory + str(i) + ".jpg"
                cv2.imwrite(file_name, img)
                last = time.time()
                i += 1
            cv2.imshow('img', img)
            cv2.waitKey(1)

#camera.stop_preview()
