from kivy.config import Config
Config.set('kivy', 'exit_on_escape', '0')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')


from kivy.app import App
from kivy.uix.popup import Popup

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
        self.robot_state_pane = ContentPane(bar_color_component=content_div_cc, background_color_component=content_background_cc, size_hint=(1.5, 1))

        controller_select = ControlSelector(button_up_cc, button_down_cc)

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

        controller_select_pane.add_widget(controller_select)
        self.command_center_pane.add_widget(self.command_center)
        tracker_pane.add_widget(self.camera_pane)
        self.robot_state_pane.add_widget(self.robot_state_image_pane)

        settings_button.add_callback(self._open_settings)
        self.settings_content_pane.add_widget(settings_pane)

        controller_select.auto_mpc_button.add_callback(controls.auto_mpc)
        controller_select.pid_button.add_callback(controls.pid)
        controller_select.open_loop_button.add_callback(controls.open_loop)
        controller_select.manual_button.add_callback(controls.manual)

        self.command_center.start_button.add_callback(controls.start_experiment)
        self.command_center.stop_button.add_callback(controls.stop_experiment)

        self.camera_pane.camera_view.add_callback(controls.camera_view)
        self.camera_pane.tracker_view.add_callback(controls.tracker_view)

        self.robot_state_image_pane.actuator0.pressurize.add_callback(controls.pressurize0)
        self.robot_state_image_pane.actuator0.depressurize.add_callback(controls.depressurize0)

        self.robot_state_image_pane.actuator1.pressurize.add_callback(controls.pressurize1)
        self.robot_state_image_pane.actuator1.depressurize.add_callback(controls.depressurize1)

        self.robot_state_image_pane.actuator2.pressurize.add_callback(controls.pressurize2)
        self.robot_state_image_pane.actuator2.depressurize.add_callback(controls.depressurize2)

        self.robot_state_image_pane.actuator3.pressurize.add_callback(controls.pressurize3)
        self.robot_state_image_pane.actuator3.depressurize.add_callback(controls.depressurize3)

        self.robot_state_image_pane.actuator4.pressurize.add_callback(controls.pressurize4)
        self.robot_state_image_pane.actuator4.depressurize.add_callback(controls.depressurize4)

        self.robot_state_image_pane.actuator5.pressurize.add_callback(controls.pressurize5)
        self.robot_state_image_pane.actuator5.depressurize.add_callback(controls.depressurize5)

        self.robot_state_image_pane.pump.add_callback(controls.pump)
        self.robot_state_image_pane.gate.add_callback(controls.gate)
        self.robot_state_image_pane.sensors.add_callback(controls.sensors)

        settings_pane.brightness.add_callback(self._adjust_brightness)
        settings_pane.contrast.add_callback(self._adjust_contrast)
        settings_pane.saturation.add_callback(self._adjust_saturation)
        settings_pane.exposure.add_callback(self._adjust_exposure)
        settings_pane.r_min.add_callback(self._adjust_r_min)
        settings_pane.r_max.add_callback(self._adjust_r_max)
        settings_pane.g_min.add_callback(self._adjust_g_min)
        settings_pane.g_max.add_callback(self._adjust_g_max)
        settings_pane.b_min.add_callback(self._adjust_b_min)
        settings_pane.b_max.add_callback(self._adjust_b_max)

        for i in range(6):
            self.robot_state_image_pane.show_pressure(i, 100.4)

        Clock.schedule_interval(self._refresh_image, 1/30)
        Clock.schedule_interval(self._background_tasks, 1/100)
        controls.app = self

        if not os.path.exists("./appdata"):
            os.mkdir("./appdata")

        if not os.path.exists("./appdata/settings.json"):
            self.command_center.frequency_text.set  ("1" )
            self.command_center.duration_text.set   ("10")
            settings_pane.brightness.set            (50  )
            settings_pane.contrast.set              (50  )
            settings_pane.saturation.set            (50  )
            settings_pane.exposure.set              (-4  )
            settings_pane.r_min.set                 (0   )
            settings_pane.r_max.set                 (255 )
            settings_pane.g_min.set                 (0   )
            settings_pane.g_max.set                 (255 )
            settings_pane.b_min.set                 (0   )
            settings_pane.b_max.set                 (255 )
            
            with open("./appdata/settings.json", "w") as f:
                json.dump(self.settings, f, indent=4)
                self.settings = json.load(f)
        else:
            with open("./appdata/settings.json", "r") as f:
                self.settings = json.load(f)
                settings_pane.brightness.set(self.settings["BRIGHTNESS"])
                settings_pane.contrast.set(self.settings["CONTRAST"])
                settings_pane.saturation.set(self.settings["SATURATION"])
                settings_pane.exposure.set(self.settings["EXPOSURE"])
                settings_pane.r_min.set(self.settings["R MIN"])
                settings_pane.r_max.set(self.settings["R MAX"])
                settings_pane.g_min.set(self.settings["G MIN"])
                settings_pane.g_max.set(self.settings["G MAX"])
                settings_pane.b_min.set(self.settings["B MIN"])
                settings_pane.b_max.set(self.settings["B MAX"])
        
        return window
    
    def on_stop(self, *args):
        with open("./appdata/settings.json", "w") as f:
            json.dump(self.settings, f, indent=4)
    
    def _open_settings(self, pressed):
        if (pressed):
            self.settings_content_pane.toggle()
            if (self.settings_content_pane.is_open()):
                self.command_center_pane.disabled = True
                self.robot_state_pane.disabled = True
            else:
                self.command_center_pane.disabled = False
                self.robot_state_pane.disabled = False
    
    def _update_log_frequency(self, text):
        self.settings["LOG FREQUENCY"] = text

    def _update_log_duration(self, text):
        self.settings["LOG DURATION"] = text
    
    def _adjust_brightness(self, min, value, max):
        controls.change_cam_settings(cv2.CAP_PROP_BRIGHTNESS, value)
        self.settings["BRIGHTNESS"] = value
    
    def _adjust_contrast(self, min, value, max):
        controls.change_cam_settings(cv2.CAP_PROP_CONTRAST, value)
        self.settings["CONTRAST"] = value
    
    def _adjust_saturation(self, min, value, max):
        controls.change_cam_settings(cv2.CAP_PROP_SATURATION, value)
        self.settings["SATURATION"] = value
    
    def _adjust_exposure(self, min, value, max):
        controls.change_cam_settings(cv2.CAP_PROP_EXPOSURE, value)
        self.settings["EXPOSURE"] = value
    
    def _adjust_r_min(self, min, value, max):
        self.settings["R MIN"] = value
    
    def _adjust_r_max(self, min, value, max):
        self.settings["R MAX"] = value

    def _adjust_g_min(self, min, value, max):
        self.settings["G MIN"] = value
    
    def _adjust_g_max(self, min, value, max):
        self.settings["G MAX"] = value
    
    def _adjust_b_min(self, min, value, max):
        self.settings["B MIN"] = value
    
    def _adjust_b_max(self, min, value, max):
        self.settings["B MAX"] = value

    def _background_tasks(self, dt):
        self.camera_pane.image.get_rgb()

    def _refresh_image(self, dt):
        result, image = controls.display_image()
        if (result):
            self.camera_pane.image.set_image(image)

app = MainWindow()

if __name__ == '__main__':
    app.run()

