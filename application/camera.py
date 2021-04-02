from picamera import PiCamera
import time

camera = PiCamera()
camera.start_preview()

time.sleep(2)

camera.capture('/home/pi/temp_photos/experiment1.jpg')

camera.stop_preview()
