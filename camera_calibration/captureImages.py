from picamera import PiCamera
import time

camera = PiCamera(sensor_mode=5, framerate=30)
camera.start_preview()

directory = "/home/pi/softwater/camera_calibration/chessboard_images/"
for i in range(50):
    time.sleep(2)
    file_name = directory + str(i) + "d.jpg"
    camera.capture(file_name, use_video_port=True)

camera.stop_preview()
