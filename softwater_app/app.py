from multiprocessing import current_process

if current_process().name == 'MainProcess':
    from kivy.config import Config
    Config.set('kivy', 'exit_on_escape', '0')
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    from kivy.app import App

    import os
    import cv2
    import numpy as np
    import json


    from util.content_classes import *
    from util.colortools import *

    import controls

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
            min_window = (1280, 720)
            Window.size = min_window
            Window.minimum_width, Window.minimum_height = min_window

            content_div_cc = ColorComponent(sunset_orange, sunset_purple, POS_LEFT, POS_RIGHT)
            content_background_cc = ColorComponent(dim_gray, dark_gray, POS_TOP_CENTER, POS_BOT_CENTER)
            select_cc = ColorComponent(sunset_orange, sunset_purple, POS_TOP_LEFT, POS_BOT_RIGHT)
            button_up_cc = ColorComponent(sunset_purple, gunmetal, POS_BOT_LEFT, POS_RIGHT)
            button_down_cc = ColorComponent(sunset_orange, gunmetal, POS_BOT_LEFT, POS_RIGHT)

            window = BoxLayout(orientation="vertical")

            main_layout = MainContentPane("./assets/title.png", "./assets/background.jpg")
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

            self.controller_select.auto_mpc_button.add_callback(controls.auto_mpc)
            self.controller_select.pid_button.add_callback(controls.pid)
            self.controller_select.open_loop_button.add_callback(controls.open_loop)
            self.controller_select.manual_button.add_callback(controls.manual)

            self.command_center.start_button.add_callback(controls.start_experiment)
            self.command_center.stop_button.add_callback(controls.stop_experiment)

            self.camera_pane.camera_view.add_callback(controls.camera_view)
            self.camera_pane.tracker_view.add_callback(controls.tracker_view)
            self.camera_pane.reset_detector.add_callback(controls.reset_detector)

            self.robot_state_image_pane.actuator0.add_pressurize_callback(controls.pressurize)
            self.robot_state_image_pane.actuator0.add_depressurize_callback(controls.depressurize)

            self.robot_state_image_pane.actuator1.add_pressurize_callback(controls.pressurize)
            self.robot_state_image_pane.actuator1.add_depressurize_callback(controls.depressurize)

            self.robot_state_image_pane.actuator2.add_pressurize_callback(controls.pressurize)
            self.robot_state_image_pane.actuator2.add_depressurize_callback(controls.depressurize)

            self.robot_state_image_pane.actuator3.add_pressurize_callback(controls.pressurize)
            self.robot_state_image_pane.actuator3.add_depressurize_callback(controls.depressurize)

            self.robot_state_image_pane.actuator4.add_pressurize_callback(controls.pressurize)
            self.robot_state_image_pane.actuator4.add_depressurize_callback(controls.depressurize)

            self.robot_state_image_pane.actuator5.add_pressurize_callback(controls.pressurize)
            self.robot_state_image_pane.actuator5.add_depressurize_callback(controls.depressurize)

            self.robot_state_image_pane.pump.add_callback(controls.pump)
            self.robot_state_image_pane.gate.add_callback(controls.gate)

            settings_pane.brightness.add_callback(controls.adjust_brightness)
            settings_pane.contrast.add_callback(controls.adjust_contrast)
            settings_pane.saturation.add_callback(controls.adjust_saturation)
            settings_pane.hue_avg.add_callback(controls.adjust_hue_average)
            settings_pane.hue_error.add_callback(controls.adjust_hue_error)
            settings_pane.saturation_low.add_callback(controls.adjust_saturation_low)
            settings_pane.saturation_high.add_callback(controls.adjust_saturation_high)
            settings_pane.value_low.add_callback(controls.adjust_value_low)
            settings_pane.value_high.add_callback(controls.adjust_value_high)
            settings_pane.gaussian_blur_x.add_callback(controls.adjust_gaussian_blur_x)
            settings_pane.gaussian_blur_y.add_callback(controls.adjust_gaussian_blur_y)
            settings_pane.circularity_min.add_callback(controls.adjust_circularity_min)
            settings_pane.circularity_max.add_callback(controls.adjust_circularity_max)
            settings_pane.area_min.add_callback(controls.adjust_area_min)
            settings_pane.area_max.add_callback(controls.adjust_area_max)
            settings_pane.inertia_min.add_callback(controls.adjust_inertia_min)
            settings_pane.inertia_max.add_callback(controls.adjust_inertia_max)

            Clock.schedule_interval(self._background_tasks, 1/30)
            Clock.schedule_interval(controls.main_callback, 1/100)
            controls.app = self

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
                    'DURATION':     20
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

                controls.detector.main_color_hue = self.settings['HUE AVG']
                controls.detector.main_color_hue_error = self.settings['HUE ERROR']
                controls.detector.main_color_low_sat = self.settings['SAT LOW']
                controls.detector.main_color_high_sat = self.settings['SAT HIGH']
                controls.detector.main_color_low_val = self.settings['VALUE LOW']
                controls.detector.main_color_high_val = self.settings['VALUE HIGH']
                controls.detector.gaussian_blur = (self.settings['GAUS BLUR X'], self.settings['GAUS BLUR Y'])
                controls.detector.params.minCircularity = float(self.settings['CIRC MIN'])
                controls.detector.params.maxCircularity = float(self.settings['CIRC MAX'])
                controls.detector.params.minArea = float(self.settings['AREA MIN'])
                controls.detector.params.maxArea = float(self.settings['AREA MAX'])
                controls.detector.params.minInertiaRatio = float(self.settings['INERTIA MIN'])
                controls.detector.params.maxInertiaRatio = float(self.settings['INERTIA MAX'])
                controls.detector.update_params()
            
            return window
        
        def on_stop(self, *args):
            with open("./appdata/settings.json", "w") as f:
                json.dump(self.settings, f, indent=4)
        
        def _open_settings(self, pressed):
            if (pressed):
                self.settings_content_pane.toggle()

        def _background_tasks(self, dt):
            result, image = controls.display_image()
            if (result):
                self.camera_pane.image.set_image(image)

    app = MainWindow()

    if __name__ == '__main__':
        app.run()

