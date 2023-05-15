from multiprocessing import current_process

if current_process().name == 'MainProcess':
    from kivy.config import Config
    Config.set('kivy', 'exit_on_escape', '0')
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    from kivy.app import App
    from kivy.core.window import Window

    import os
    #os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
    import cv2
    import numpy as np
    import json

    import datetime
    from rate import Rate
    from detect import RobotDetector
    from controller import ControllerHandler
    import manual
    import simple_controller
    import visual_servo
    import ampc_controller
    from usbcom import USBMessageBroker
    import struct
    import time
    from camera import Camera


    from util.content_classes import *
    from util.colortools import *

    white = Color(255, 255, 255)
    mostly_white = Color(240, 240, 240)
    light_gray = Color(200, 200, 200)
    gray = Color(178, 190, 195)
    leafy_green = Color(109, 163, 39)
    dark_green = Color(44, 74, 4)
    sunset_orange = Color(207, 94, 37)
    sunset_purple = Color(181, 66, 201)
    gunmetal = Color(45, 52, 54)
    dim_gray = Color(99, 110, 114)
    dark_gray = Color(70, 70, 70)

    class MainWindow(App):
        def build(self):
            global backend

            min_window = (1280, 720)
            Window.size = min_window
            Window.minimum_width, Window.minimum_height = min_window

            content_div_cc = ColorComponent(sunset_orange, sunset_purple, POS_LEFT, POS_RIGHT)
            content_background_cc = ColorComponent(light_gray, gray, POS_TOP_CENTER, POS_BOT_CENTER)
            select_cc = ColorComponent(sunset_orange, sunset_purple, POS_TOP_LEFT, POS_BOT_RIGHT)
            button_up_cc = ColorComponent(sunset_purple, gunmetal, POS_BOT_LEFT, POS_RIGHT)
            button_down_cc = ColorComponent(sunset_orange, gunmetal, POS_BOT_LEFT, POS_RIGHT)

            window = BoxLayout(orientation="vertical")

            main_layout = MainContentPane("./assets/title.png", "./assets/white_background.jpg")
            title_layout = FloatLayout(size_hint=(1, 0.15), pos_hint={"x": 0, "top": 1})

            title = ImagePane("./assets/title.png", size_hint=(0.3, 0.9), pos_hint={"x": 0.05, "center_y": 0.5})
            settings_button = IconButton("./assets/settings.png", "./assets/settings_pressed.png", size_hint=(0.1, 0.9), pos_hint={"right": 1, "center_y": 0.5})

            content_top = BoxLayout(orientation="horizontal", padding=20, spacing=40, size_hint=(1, 0.35), pos_hint={"center_x": 0.5, "y": 0.5})
            content_bottom = BoxLayout(orientation="horizontal", padding=20, spacing=40, size_hint=(1, 0.5), pos_hint={"center_x": 0.5, "y": 0})
            self.settings_content_pane = HiddenContentPane(size_hint=(0.4, 0.75), pos_hint={"right": 1}, bar_color_component=content_div_cc, background_color_component=content_background_cc)
            settings_pane = SettingsPane()

            controller_select_pane = ContentPane(bar_color_component=content_div_cc, background_color_component=content_background_cc, size_hint=(2, 1))
            self.command_center_pane = ContentPane(bar_color_component=content_div_cc, background_color_component=content_background_cc)
            tracker_pane = ContentPane(bar_color_component=content_div_cc, background_color_component=content_background_cc)
            self.robot_state_pane = ContentPane(bar_color_component=content_div_cc, background_color_component=content_background_cc)

            self.controller_select = ControlSelector(button_up_cc, button_down_cc)

            self.command_center = CommandCenter(button_up_cc, button_down_cc)

            self.robot_state_image_pane = RobotImagePane(
                "./assets/robot.png",
                button_up_cc,
                button_down_cc,
                "./assets/pressurize.png",
                "./assets/pressurize_off.png",
                "./assets/depressurize.png",
                "./assets/depressurize_off.png")
            
            self.camera_pane = CameraPane(button_up_cc, button_down_cc, select_cc)

            # asm
            window.add_widget(main_layout)

            main_layout.add_widget(title_layout)
            main_layout.add_widget(content_top)
            main_layout.add_widget(content_bottom)
            main_layout.add_widget(self.settings_content_pane)

            title_layout.add_widget(title)
            title_layout.add_widget(settings_button)

            content_top.add_widget(controller_select_pane)
            content_top.add_widget(self.command_center_pane)

            content_bottom.add_widget(tracker_pane)
            content_bottom.add_widget(self.robot_state_pane)

            controller_select_pane.add_widget(self.controller_select)
            self.command_center_pane.add_widget(self.command_center)
            tracker_pane.add_widget(self.camera_pane)
            self.robot_state_pane.add_widget(self.robot_state_image_pane)

            settings_button.add_callback(self._open_settings)
            self.settings_content_pane.add_widget(settings_pane)

            self.controller_select.auto_mpc_button.add_callback(backend.auto_mpc)
            self.controller_select.pid_button.add_callback(backend.pid)
            self.controller_select.open_loop_button.add_callback(backend.open_loop)
            self.controller_select.manual_button.add_callback(backend.manual)

            self.command_center.connect.add_callback(backend.connect)
            self.command_center.start_button.add_callback(backend.start_experiment)
            self.command_center.stop_button.add_callback(backend.stop_experiment)
            self.command_center.frequency_text.add_callback(backend.adjust_frequency)
            self.command_center.duration_text.add_callback(backend.adjust_duration)

            self.camera_pane.camera_view.add_callback(backend.camera_view)
            self.camera_pane.tracker_view.add_callback(backend.tracker_view)
            self.camera_pane.reset_detector.add_callback(backend.reset_detector)

            self.robot_state_image_pane.actuator0.add_pressurize_callback(backend.pressurize)
            self.robot_state_image_pane.actuator0.add_depressurize_callback(backend.depressurize)

            self.robot_state_image_pane.actuator1.add_pressurize_callback(backend.pressurize)
            self.robot_state_image_pane.actuator1.add_depressurize_callback(backend.depressurize)

            self.robot_state_image_pane.actuator2.add_pressurize_callback(backend.pressurize)
            self.robot_state_image_pane.actuator2.add_depressurize_callback(backend.depressurize)

            self.robot_state_image_pane.actuator3.add_pressurize_callback(backend.pressurize)
            self.robot_state_image_pane.actuator3.add_depressurize_callback(backend.depressurize)

            self.robot_state_image_pane.actuator4.add_pressurize_callback(backend.pressurize)
            self.robot_state_image_pane.actuator4.add_depressurize_callback(backend.depressurize)

            self.robot_state_image_pane.actuator5.add_pressurize_callback(backend.pressurize)
            self.robot_state_image_pane.actuator5.add_depressurize_callback(backend.depressurize)

            self.robot_state_image_pane.pump.add_callback(backend.pump)
            self.robot_state_image_pane.gate.add_callback(backend.gate)

            settings_pane.brightness.add_callback(backend.adjust_brightness)
            settings_pane.contrast.add_callback(backend.adjust_contrast)
            settings_pane.saturation.add_callback(backend.adjust_saturation)
            settings_pane.hue_avg.add_callback(backend.adjust_hue_average)
            settings_pane.hue_error.add_callback(backend.adjust_hue_error)
            settings_pane.saturation_low.add_callback(backend.adjust_saturation_low)
            settings_pane.saturation_high.add_callback(backend.adjust_saturation_high)
            settings_pane.value_low.add_callback(backend.adjust_value_low)
            settings_pane.value_high.add_callback(backend.adjust_value_high)
            settings_pane.gaussian_blur_x.add_callback(backend.adjust_gaussian_blur_x)
            settings_pane.gaussian_blur_y.add_callback(backend.adjust_gaussian_blur_y)
            settings_pane.circularity_min.add_callback(backend.adjust_circularity_min)
            settings_pane.circularity_max.add_callback(backend.adjust_circularity_max)
            settings_pane.area_min.add_callback(backend.adjust_area_min)
            settings_pane.area_max.add_callback(backend.adjust_area_max)
            settings_pane.inertia_min.add_callback(backend.adjust_inertia_min)
            settings_pane.inertia_max.add_callback(backend.adjust_inertia_max)

            Clock.schedule_interval(self._background_tasks, 1/30)
            Clock.schedule_interval(backend.main_callback, 1/100)
            backend.app = self

            if not os.path.exists("./appdata"):
                os.mkdir("./appdata")

            if not os.path.exists("./appdata/settings.json"):
                settings = dict({
                    'BRIGHTNESS':   50,
                    'CONTRAST':     0,
                    'SATURATION':   0,
                    'HUE AVG':      0,
                    'HUE ERROR':    3,
                    'SAT LOW':      60,
                    'SAT HIGH':     255,
                    'VALUE LOW':    60,
                    'VALUE HIGH':   245,
                    'GAUS BLUR X':  25,
                    'GAUS BLUR Y':  25,
                    'CIRC MIN':     0.6,
                    'CIRC MAX':     'inf',
                    'AREA MIN':     100,
                    'AREA MAX':     'inf',
                    'INERTIA MIN':  0.2,
                    'INERTIA MAX':  'inf',
                    'FREQUENCY':    2,
                    'DURATION':     20,
                    'TARGET IDX':   0
                })
                
                with open("./appdata/settings.json", "w") as f:
                    json.dump(settings, f, indent=4)
            
            with open("./appdata/settings.json", "r") as f:
                self.settings = json.load(f)
                settings_pane.brightness.set(self.settings['BRIGHTNESS'])
                settings_pane.contrast.set(self.settings['CONTRAST'])
                settings_pane.saturation.set(self.settings['SATURATION'])
                settings_pane.hue_avg.text = str(self.settings['HUE AVG'])
                settings_pane.hue_error.text = str(self.settings['HUE ERROR'])
                settings_pane.saturation_low.text = str(self.settings['SAT LOW'])
                settings_pane.saturation_high.text = str(self.settings['SAT HIGH'])
                settings_pane.value_low.text = str(self.settings['VALUE LOW'])
                settings_pane.value_high.text = str(self.settings['VALUE HIGH'])
                settings_pane.gaussian_blur_x.text = str(self.settings['GAUS BLUR X'])
                settings_pane.gaussian_blur_y.text = str(self.settings['GAUS BLUR Y'])
                settings_pane.circularity_min.text = str(self.settings['CIRC MIN'])
                settings_pane.circularity_max.text = str(self.settings['CIRC MAX'])
                settings_pane.area_min.text = str(self.settings['AREA MIN'])
                settings_pane.area_max.text = str(self.settings['AREA MAX'])
                settings_pane.inertia_min.text = str(self.settings['INERTIA MIN'])
                settings_pane.inertia_max.text = str(self.settings['INERTIA MAX'])
                self.command_center.frequency_text.text = str(self.settings['FREQUENCY'])
                self.command_center.duration_text.text = str(self.settings['DURATION'])
                self.controller_select.target.text = str(self.settings['TARGET IDX'])

                backend.detector.main_color_hue = self.settings['HUE AVG']
                backend.detector.main_color_hue_error = self.settings['HUE ERROR']
                backend.detector.main_color_low_sat = self.settings['SAT LOW']
                backend.detector.main_color_high_sat = self.settings['SAT HIGH']
                backend.detector.main_color_low_val = self.settings['VALUE LOW']
                backend.detector.main_color_high_val = self.settings['VALUE HIGH']
                backend.detector.gaussian_blur = (self.settings['GAUS BLUR X'], self.settings['GAUS BLUR Y'])
                backend.detector.params.minCircularity = float(self.settings['CIRC MIN'])
                backend.detector.params.maxCircularity = float(self.settings['CIRC MAX'])
                backend.detector.params.minArea = float(self.settings['AREA MIN'])
                backend.detector.params.maxArea = float(self.settings['AREA MAX'])
                backend.detector.params.minInertiaRatio = float(self.settings['INERTIA MIN'])
                backend.detector.params.maxInertiaRatio = float(self.settings['INERTIA MAX'])
                backend.detector.update_params()
            
            return window
        
        def on_stop(self, *args):
            global backend

            with open("./appdata/settings.json", "w") as f:
                json.dump(self.settings, f, indent=4)
            backend.camera.stop()
        
        def _open_settings(self, pressed):
            if (pressed):
                self.settings_content_pane.toggle()

        def _background_tasks(self, dt):
            global backend

            result, image = backend.display_image()
            if (result):
                self.camera_pane.image.set_image(image)

    app = MainWindow()

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

    class AppBackend:
        handler = ControllerHandler()
        detector = RobotDetector()
        camera = Camera(1920, 1280)
        link = None

        is_camera_view = True
        raw_image = None
        tracking = False
        camera_image = None
        tracker_image = None
        dc_image = cv2.imread('./assets/disconnected.png')
        experiment_dir = './experiments'
        data_dir_name = ''

        pvals = None
        pipe_data = None

        timeout = 2
        ping_rate = Rate(2)
        last_ping_start = 0
        last_ping_return = 0

        def __init__(self) -> None:
            self.detector.set_dims(*self.camera.dims())

        def __del__(self) -> None:
            self.camera.stop()

        def new_experiment_dir(self, name):
            idx = check_int(app.controller_select.target.text)
            new_name = name + " IDX" + str(idx)
            if not os.path.exists(self.experiment_dir):
                os.mkdir(self.experiment_dir)
            timestamp = datetime.datetime.now()
            folder = f"{self.experiment_dir}/{new_name} {timestamp.hour}-{timestamp.minute}-{timestamp.second} {timestamp.month}-{timestamp.day}-{timestamp.year}/"
            print("making experiment_dir")
            os.mkdir(folder)
            return folder

        def package_data(self, m, p, img):
            m = self.detector.pix2world(m)

            x_home = m[0][0]
            y_home = m[0][1]
            origin = [x_home, y_home]

            x = []
            for i in range(0, self.detector.max_pts):
                x.append(m[i][0] - x_home)
                x.append(y_home - m[i][1])

            return (time.perf_counter(), origin, x, p, self.detector.robot_segments, img)

        def main_callback(self, dt):
            img = self.camera.get()
            if img is not None:
                self.raw_image = img
                self.tracking, self.camera_image, self.tracker_image = self.detector.detect(img)
            
            app.camera_pane.set_detector_status(self.tracking)

            if self.link:
                self.link.update()

                app.command_center.set_receiver_status(self.link.connected())
                if self.link.connected():
                    if self.ping_rate.ready():
                        self.link.send(0)
                        self.last_ping_start = time.time()
                    if time.time() - self.last_ping_return > self.timeout:
                        app.command_center.set_robot_status(False, "N/A ms")
                else:
                    app.command_center.set_robot_status(False, "N/A ms")
                
                while len(self.link.messages) > 0:
                    msg = self.link.messages.pop()
                    if msg.type == 1:
                        self.last_ping_return = time.time()
                        self.ping = time.time() - self.last_ping_start
                        app.command_center.set_robot_status(True, "{:.2f} ms".format(self.ping * 1000))
                    if msg.type == 2:
                        self.pvals = struct.unpack(f'<{"f" * int(len(msg.data) / 4)}', msg.data)
                        for (i, val) in enumerate(self.pvals):
                            app.robot_state_image_pane.show_pressure(i, val)
                
                self.link.update()
                    
            while True:
                output = self.handler.pipe_out()
                if not output:
                    break
                if not self.link:
                    continue
                type, data = output
                if type == 'robot':
                    if 'set solenoids' in data['command'].keys():
                        u = data['command']['set solenoids']
                        arr = struct.pack('%s?' % len(u), *u)
                        if self.link:
                            self.link.send(3, arr)
                        print(u)
                elif type == 'app':
                    if not self.tracking:
                        self.handler.controller.stop()
                    if data == 'get data' and self.raw_image is not None and self.pvals is not None:
                        self.handler.pipe_in(self.package_data(self.detector.tracker.objects, self.pvals, self.raw_image))
            
        def auto_mpc(self, pressed):
            if pressed:
                print('mode: auto mpc')
                self.handler.set_controller(ampc_controller.controller)
                self.data_dir_name = 'Auto_MPC'
        
        def pid(self, pressed):
            if pressed:
                print('mode: visual servo')
                self.handler.set_controller(visual_servo.controller)
                self.data_dir_name = 'Visual_Servo'

        def open_loop(self, pressed):
            if pressed:
                print('mode: open loop')
                self.handler.set_controller(simple_controller.controller)
                self.data_dir_name = 'Open_Loop'

        def manual(self, pressed):
            if pressed:
                print('mode: manual')
                self.handler.set_controller(manual.controller)
                self.data_dir_name = 'Manual'
        
        def connect(self, pressed):
            if pressed:
                try:
                    temp = USBMessageBroker(app.command_center.com_select.text, baudrate=500000)
                    self.link = temp
                except:
                    print('usb error')
                try:
                    src = int(app.command_center.cam_select.text)
                    if self.camera.running():
                        self.camera.change_source(src)
                    else:
                        self.camera.start(src)
                except Exception as e:
                    print('bad input ', e)
        
        def start_experiment(self, pressed):
            if pressed:
                if self.handler.controller is not None:
                    idx = check_int(app.controller_select.target.text)
                    if idx is None:
                        app.command_center.start_button.state = "normal"
                    self.handler.controller.data_dir = self.new_experiment_dir(self.data_dir_name)
                    targ = self.handler.controller.convert_idx(idx)
                    self.handler.controller.prepare(targ)
                    self.handler.controller.rate = Rate(float(app.command_center.frequency_text.text))
                    self.handler.controller.timeout = float(app.command_center.duration_text.text)
                    self.handler.start()
        
        def stop_experiment(self, pressed):
            if pressed and self.handler.controller is not None:
                self.handler.controller.stop()
        
        def camera_view(self, pressed):
            if pressed:
                self.is_camera_view = not self.is_camera_view
        
        def tracker_view(self, pressed):
            if pressed:
                self.is_camera_view = not self.is_camera_view
        
        def reset_detector(self, pressed):
            if pressed:
                self.detector.reset()
        
        def display_image(self):
            if not self.camera.running():
                return True, self.dc_image
            if self.is_camera_view:
                return self.camera_image is not None, self.camera_image
            else:
                return self.tracker_image is not None, self.tracker_image
            
        def pressurize(self, id, pressed):
            if self.link:
                stage = id // 2
                valve = 2 * (id % 2)
                self.link.send(4, struct.pack('>BB?', stage, valve, pressed))

        def depressurize(self, id, pressed):
            if self.link:
                stage = id // 2
                valve = 2 * (id % 2) + 1            
                self.link.send(4, struct.pack('>BB?', stage, valve, pressed))

        def pump(self, pressed):
            if self.link:
                self.link.send(5, struct.pack('>?', pressed))
        
        def gate(self, pressed):
            if self.link:
                self.link.send(6, struct.pack('>?', pressed))

        def adjust_brightness(self, min, value, max):
            self.camera.set(cv2.CAP_PROP_BRIGHTNESS, value)
            app.settings['BRIGHTNESS'] = value
        
        def adjust_contrast(self, min, value, max):
            self.camera.set(cv2.CAP_PROP_CONTRAST, value)
            app.settings['CONTRAST'] = value
        
        def adjust_saturation(self, min, value, max):
            self.camera.set(cv2.CAP_PROP_SATURATION, value)
            app.settings['SATURATION'] = value
        
        def adjust_hue_average(self, instance, text):
            value = check_int(text, 0, 180)
            if value is None:
                instance.text = str(app.settings['HUE AVG'])
            else:
                self.detector.main_color_hue = value
                app.settings['HUE AVG'] = value
        
        def adjust_hue_error(self, instance, text):
            value = check_int(text, 0, 90)
            if value is None:
                instance.text = str(app.settings['HUE ERROR'])
            else:
                self.detector.main_color_hue_error = value
                app.settings['HUE ERROR'] = value

        def adjust_saturation_low(self, instance, text):
            value = check_int(text, 0, 255)
            if value is None:
                instance.text = str(app.settings['SAT LOW'])
            else:
                self.detector.main_color_low_sat = value
                app.settings['SAT LOW'] = value

        def adjust_saturation_high(self, instance, text):
            value = check_int(text, 0, 255)
            if value is None:
                instance.text = str(app.settings['SAT HIGH'])
            else:
                self.detector.main_color_high_sat
                app.settings['SAT HIGH'] = value

        def adjust_value_low(self, instance, text):
            value = check_int(text, 0, 255)
            if value is None:
                instance.text = str(app.settings['VALUE LOW'])
            else:
                self.detector.main_color_low_val = value
                app.settings['VALUE LOW'] = value

        def adjust_value_high(self, instance, text):
            value = check_int(text, 0, 255)
            if value is None:
                instance.text = str(app.settings['VALUE HIGH'])
            else:
                self.detector.main_color_high_val = value
                app.settings['VALUE HIGH'] = value

        def adjust_gaussian_blur_x(self, instance, text):
            value = check_int(text, 0, 255, True)
            if value is None:
                instance.text = str(app.settings['GAUS BLUR X'])
            else:
                self.detector.gaussian_blur = (value, self.detector.gaussian_blur[1])
                app.settings['GAUS BLUR X'] = value

        def adjust_gaussian_blur_y(self, instance, text):
            value = check_int(text, 0, 255, True)
            if value is None:
                instance.text = str(app.settings['GAUS BLUR Y'])
            else:
                self.detector.gaussian_blur = (self.detector.gaussian_blur[0], value)
                app.settings['GAUS BLUR Y'] = value

        def adjust_circularity_min(self, instance, text):
            value = check_ufloat(text)
            if value is None:
                instance.text = str(app.settings['CIRC MIN'])
            else:
                self.detector.params.minCircularity = value
                self.detector.update_params()
                app.settings['CIRC MIN'] = value

        def adjust_circularity_max(self, instance, text):
            value = check_ufloat(text)
            if value is None:
                instance.text = str(app.settings['CIRC MAX'])
            else:
                self.detector.params.maxCircularity = value
                self.detector.update_params()
                app.settings['CIRC MAX'] = value

        def adjust_area_min(self, instance, text):
            value = check_ufloat(text)
            if value is None:
                instance.text = str(app.settings['AREA MIN'])
            else:
                self.detector.params.minArea = value
                self.detector.update_params()
                app.settings['AREA MIN'] = value

        def adjust_area_max(self, instance, text):
            value = check_ufloat(text)
            if value is None:
                instance.text = str(app.settings['AREA MAX'])
            else:
                self.detector.params.maxArea = value
                self.detector.update_params()
                app.settings['AREA MAX'] = value

        def adjust_inertia_min(self, instance, text):
            value = check_ufloat(text)
            if value is None:
                instance.text = str(app.settings['INERTIA MIN'])
            else:
                self.detector.params.minInertiaRatio = value
                self.detector.update_params()
                app.settings['INERTIA MIN'] = value

        def adjust_inertia_max(self, instance, text):
            value = check_ufloat(text)
            if value is None:
                instance.text = str(app.settings['INERTIA MAX'])
            else:
                self.detector.params.maxInertiaRatio = value
                self.detector.update_params()
                app.settings['INERTIA MAX'] = value

        def adjust_frequency(self, instance, text):
            value = check_ufloat(text)
            if value is None:
                instance.text = str(app.settings['FREQUENCY'])
            else:
                app.settings['FREQUENCY'] = value

        def adjust_duration(self, instance, text):
            value = check_ufloat(text)
            if value is None:
                instance.text = str(app.settings['DURATION'])
            else:
                app.settings['DURATION'] = value

    backend = AppBackend()

    if __name__ == '__main__':
        app.run()

