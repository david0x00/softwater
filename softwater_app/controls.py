from app import app
import cv2
from datalink import DataLink
from detect import RobotDetector
from controller import ControllerHandler
import simple_controller
import visual_servo

is_camera_view = True
link = DataLink("App", False, "169.254.11.63")
detector = RobotDetector()

camera_image = None
tracker_image = None
dc_image = cv2.imread("./assets/disconnected.png")

first_connect = True

handler = ControllerHandler()

pipe_data = None

def package_data(m, p):
    x = []
    x += p

    m = detector.pix2world(m)

    x_home = m[0][0]
    y_home = m[0][1]

    for i in range(1, detector.robot_segments):
        x.append(m[i][0] - x_home)
        x.append(y_home - m[i][1])

    return x

def main_callback(dt):
    global camera_image, tracker_image, pipe_data, first_connect

    link.update()

    app.command_center.set_robot_status(link.connected(), link.latency(string=True))

    if link.data_available():
        msg = link.get()['data']
        if 'data' in msg.keys():
            data = msg['data']
            if 'keyframe' in data.keys():
                timestamp, img, pvalues = data['keyframe']
                tracking, camera_image, tracker_image = detector.detect(img)
                app.camera_pane.set_detector_status(tracking)
                for sensor in range(len(pvalues)):
                    app.robot_state_image_pane.show_pressure(sensor, pvalues[sensor])

                if tracking:
                    x = package_data(detector.tracker.objects, pvalues)
                    pipe_data = ([timestamp], x, img)
                else:
                    pipe_data = None
    
    if link.connected():
        if first_connect:
            change_cam_settings(cv2.CAP_PROP_WB_TEMPERATURE, 10000)
            change_cam_settings(cv2.CAP_PROP_AUTO_WB, 1)
            
            adjust_brightness(0, app.settings['BRIGHTNESS'], 0)
            adjust_contrast(0, app.settings['CONTRAST'], 0)
            adjust_saturation(0, app.settings['SATURATION'], 0)
            first_connect = False
        if handler.is_alive():
            while True:
                output = handler.pipe_out()
                if output is None:
                    break
                type, data = output
                if type == 'robot':
                    link.send(data)
                elif type == 'app':
                    if data == 'get data' and pipe_data is not None:
                        handler.pipe_in(pipe_data)
        app.camera_pane.image.can_zoom = True
    else:
        camera_image = tracker_image = dc_image
        app.camera_pane.image.reset_zoom()
        app.camera_pane.image.can_zoom = False
        first_connect = True
    
    link.update()

def auto_mpc(pressed):
    print("Auto MPC:", pressed)
    if pressed:
        global handler
        handler.set_controller(simple_controller.controller)

def pid(pressed):
    print("PID:", pressed)
    if pressed:
        global handler
        handler.set_controller(visual_servo.controller)

def open_loop(pressed):
    print("Open Loop:", pressed)
    if pressed:
        print(app.controller_select.open_loop_selector.file_path)

def manual(pressed):
    print("Manual:", pressed)

def start_experiment(pressed):
    print("Start Experiment:", pressed)
    if (pressed):
        '''log = app.command_center.log_button.state == "down"
        
        try:
            log_frequency = float(app.command_center.frequency_text.text)
            log_duration = float(app.command_center.duration_text.text)
        except:
            log = False
        
        print("LOG:", log)
        if log:
            print("Frequency:", log_frequency)
            print("Duration:", log_duration)'''
        global handler
        if handler.controller is not None:
            handler.controller.data_dir = "./experiments/"
            handler.controller.prepare((9, 27))
            handler.start()

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

def reset_detector(pressed):
    global detector
    if pressed:
        detector.reset()

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

def adjust_brightness(min, value, max):
    change_cam_settings(cv2.CAP_PROP_BRIGHTNESS, value)
    app.settings['BRIGHTNESS'] = value

def adjust_contrast(min, value, max):
    change_cam_settings(cv2.CAP_PROP_CONTRAST, value)
    app.settings['CONTRAST'] = value

def adjust_saturation(min, value, max):
    change_cam_settings(cv2.CAP_PROP_SATURATION, value)
    app.settings['SATURATION'] = value

def check_ufloat(text):
    try:
        value = float(text)
        if value >= 0:
            return value
    except:
        pass
    return None

def check_int(text, min=None, max=None, is_odd=None):
    try:
        value = int(text)
        passes = True
        if min is not None and value < min:
            passes = False
        elif max is not None and value > max:
            passes = False
        elif is_odd is not None and (value % 2) == 0:
            passes = False
        if passes:
            return value
    except:
        pass
    return None

def adjust_hue_average(instance, text):
    value = check_int(text, 0, 180)
    if value is None:
        instance.text = str(app.settings['HUE AVG'])
    else:
        detector.main_color_hue = value
        app.settings['HUE AVG'] = value

def adjust_hue_error(instance, text):
    value = check_int(text, 0, 90)
    if value is None:
        instance.text = str(app.settings['HUE ERROR'])
    else:
        detector.main_color_hue_error = value
        app.settings['HUE ERROR'] = value

def adjust_saturation_low(instance, text):
    value = check_int(text, 0, 255)
    if value is None:
        instance.text = str(app.settings['SAT LOW'])
    else:
        detector.main_color_low_sat = value
        app.settings['SAT LOW'] = value

def adjust_saturation_high(instance, text):
    value = check_int(text, 0, 255)
    if value is None:
        instance.text = str(app.settings['SAT HIGH'])
    else:
        detector.main_color_high_sat
        app.settings['SAT HIGH'] = value

def adjust_value_low(instance, text):
    value = check_int(text, 0, 255)
    if value is None:
        instance.text = str(app.settings['VALUE LOW'])
    else:
        detector.main_color_low_val = value
        app.settings['VALUE LOW'] = value

def adjust_value_high(instance, text):
    value = check_int(text, 0, 255)
    if value is None:
        instance.text = str(app.settings['VALUE HIGH'])
    else:
        detector.main_color_high_val = value
        app.settings['VALUE HIGH'] = value

def adjust_gaussian_blur_x(instance, text):
    value = check_int(text, 0, 255, True)
    if value is None:
        instance.text = str(app.settings['GAUS BLUR X'])
    else:
        detector.gaussian_blur = (value, detector.gaussian_blur[1])
        app.settings['GAUS BLUR X'] = value

def adjust_gaussian_blur_y(instance, text):
    value = check_int(text, 0, 255, True)
    if value is None:
        instance.text = str(app.settings['GAUS BLUR Y'])
    else:
        detector.gaussian_blur = (detector.gaussian_blur[0], value)
        app.settings['GAUS BLUR Y'] = value

def adjust_circularity_min(instance, text):
    value = check_ufloat(text)
    if value is None:
        instance.text = str(app.settings['CIRC MIN'])
    else:
        detector.params.minCircularity = value
        detector.update_params()
        app.settings['CIRC MIN'] = value

def adjust_circularity_max(instance, text):
    value = check_ufloat(text)
    if value is None:
        instance.text = str(app.settings['CIRC MAX'])
    else:
        detector.params.maxCircularity = value
        detector.update_params()
        app.settings['CIRC MAX'] = value

def adjust_area_min(instance, text):
    value = check_ufloat(text)
    if value is None:
        instance.text = str(app.settings['AREA MIN'])
    else:
        detector.params.minArea = value
        detector.update_params()
        app.settings['AREA MIN'] = value

def adjust_area_max(instance, text):
    value = check_ufloat(text)
    if value is None:
        instance.text = str(app.settings['AREA MAX'])
    else:
        detector.params.maxArea = value
        detector.update_params()
        app.settings['AREA MAX'] = value

def adjust_inertia_min(instance, text):
    value = check_ufloat(text)
    if value is None:
        instance.text = str(app.settings['INERTIA MIN'])
    else:
        detector.params.minInertiaRatio = value
        detector.update_params()
        app.settings['INERTIA MIN'] = value

def adjust_inertia_max(instance, text):
    value = check_ufloat(text)
    if value is None:
        instance.text = str(app.settings['INERTIA MAX'])
    else:
        detector.params.maxInertiaRatio = value
        detector.update_params()
        app.settings['INERTIA MAX'] = value
    