from app import app
import cv2
from camera import Camera

cam = Camera(1920, 1080)
cam.new_stream()
cam.start()
is_camera_view = True

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
    print("Camera View:", pressed)
    if (pressed):
        global is_camera_view
        is_camera_view = not is_camera_view

def tracker_view(pressed):
    print("Tracker View:", pressed)
    if (pressed):
        global is_camera_view
        is_camera_view = not is_camera_view

def display_image():
    result, image = cam.get(0)
    if result and not is_camera_view:
        lower_bound = (app.settings["B MIN"], app.settings["G MIN"], app.settings["R MIN"])
        upper_bound = (app.settings["B MAX"], app.settings["G MAX"], app.settings["R MAX"])
        image = cv2.inRange(image, lower_bound, upper_bound)
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    return result, image
        
def change_cam_settings(setting, value):
    cam.set(setting, value)

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

def gate(pressed):
    print("Gate:", pressed)

def sensors(pressed):
    print("Sensors:", pressed)