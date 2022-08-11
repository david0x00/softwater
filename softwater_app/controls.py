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
                print(pvalues)
                keypoints, tracker_image = detector.detect(img)
                camera_image = cv2.drawKeypoints(img, keypoints, np.zeros((1, 1)), (0, 255, 0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

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
    print("Camera View:", pressed)
    if (pressed):
        is_camera_view = not is_camera_view

def tracker_view(pressed):
    global is_camera_view
    print("Tracker View:", pressed)
    if (pressed):
        is_camera_view = not is_camera_view

def display_image():
    if is_camera_view:
        if camera_image is not None:
            return True, camera_image
    else:
        if tracker_image is not None:
            return True, cv2.cvtColor(tracker_image, cv2.COLOR_GRAY2BGR)
    return False, None
        
def change_cam_settings(setting, value):
    pass

def pressurize0(pressed):
    print("Pressurize0:", pressed)
    app.robot_state_image_pane.show_pressure(0, 105.2)

def depressurize0(pressed):
    print("Depressurize0:", pressed)
    app.robot_state_image_pane.show_pressure(0, 100.2)

def pressurize1(pressed):
    print("Pressurize1:", pressed)

def depressurize1(pressed):
    print("Depressurize1:", pressed)

def pressurize2(pressed):
    print("Pressurize2:", pressed)

def depressurize2(pressed):
    print("Depressurize2:", pressed)

def pressurize3(pressed):
    print("Pressurize3:", pressed)

def depressurize3(pressed):
    print("Depressurize3:", pressed)

def pressurize4(pressed):
    print("Pressurize4:", pressed)

def depressurize4(pressed):
    print("Depressurize4:", pressed)  

def pressurize5(pressed):
    print("Pressurize5:", pressed)

def depressurize5(pressed):
    print("Depressurize5:", pressed)

def pump(pressed):
    print("Pump:", pressed)
    if link.connected():
        link.send({'command': {''}})

def gate(pressed):
    print("Gate:", pressed)

def sensors(pressed):
    print("Sensors:", pressed)
