from operator import is_
from re import L
from app import app
import cv2
from camera import Camera
from datalink import DataLink
from detect import RobotDetector
import numpy as np
from rate import Rate

is_camera_view = True
link = DataLink("App", False, "169.254.11.63")
detector = RobotDetector()

camera_image = None
tracker_image = None
pvalues = [0, 0, 0, 0, 0, 0]

ask_rate = Rate(10)

def main_callback(dt):
    global camera_image, tracker_image, pvalues

    link.update()

    app.command_center.set_robot_status(link.connected(), link.latency(string=True))

    if link.connected():
        if ask_rate.ready():
            link.send({'command': {'get keyframe': None}})

    if link.data_available():
        msg = link.get()['data']
        if 'data' in msg.keys():
            data = msg['data']
            if 'keyframe' in data.keys():
                img, pvalues = data['keyframe']
                keypoints, tracker_image = detector.detect(img)
                camera_image = img
                for sensor in range(len(pvalues)):
                    app.robot_state_image_pane.show_pressure(sensor, pvalues[sensor])

    link.update()

def auto_mpc(pressed):
    print("Auto MPC:", pressed)

def pid(pressed):
    print("PID:", pressed)

def open_loop(pressed):
    print("Open Loop:", pressed)

def manual(pressed):
    print("Manual:", pressed)

def start_experiment(pressed):
    print("Start Experiment:", pressed)
    if (pressed):
        log = app.command_center.log_button.state == "down"
        
        try:
            log_frequency = float(app.command_center.frequency_text.text)
            log_duration = float(app.command_center.duration_text.text)
        except:
            log = False
        
        print("LOG:", log)
        if log:
            print("Frequency:", log_frequency)
            print("Duration:", log_duration)

def stop_experiment(pressed):
    print("Stop Experiment: ", pressed)

def camera_view(pressed):
    global is_camera_view
    if (pressed):
        is_camera_view = not is_camera_view

def tracker_view(pressed):
    global is_camera_view
    if (pressed):
        is_camera_view = not is_camera_view

def display_image():
    if is_camera_view:
        if camera_image is not None:
            return True, camera_image
    else:
        if tracker_image is not None:
            return True, tracker_image
    return False, None
        
def change_cam_settings(setting, value):
    link.send({'command': {'cam setting': (setting, value)}})

def pressurize(id, pressed):
    link.send({'command': {'pressurize': (id, pressed)}})

def depressurize(id, pressed):
    link.send({'command': {'depressurize': (id, pressed)}})

def pump(pressed):
    link.send({'command': {'pump': pressed}})

def gate(pressed):
    link.send({'command': {'gate': pressed}})
