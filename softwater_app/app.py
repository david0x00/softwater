import sys
sys.path.insert(1, './utils')

from kivy.config import Config
Config.set('kivy', 'exit_on_escape', '0')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')


from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.clock import Clock

import cv2
import numpy as np

from util.kivyclasses import *
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

        window = BoxLayout(orientation="vertical")

        content_div_cc = ColorComponent(sunset_orange, sunset_purple, POS_LEFT, POS_RIGHT, txtsize=2)
        content_background_cc = ColorComponent(dim_gray, dark_gray, POS_TOP_CENTER, POS_BOT_CENTER)

        main_layout = MainContentPane("./assets/title.png", "./assets/background.jpg")

        title = ImagePane("./assets/title.png", size_hint=(0.3, 0.1), pos_hint={"x": 0.05, "top": 0.95})

        content_top = BoxLayout(orientation="horizontal", padding=20, spacing=40, size_hint=(1, 0.35), pos_hint={"center_x": 0.5, "y": 0.5})
        content_bottom = BoxLayout(orientation="horizontal", padding=20, spacing=40, size_hint=(1, 0.5), pos_hint={"center_x": 0.5, "y": 0})

        controller_select_pane = ContentPane(bar_color_component=content_div_cc, background_color_component=content_background_cc, size_hint=(2, 1))
        command_center_pane = ContentPane(bar_color_component=content_div_cc, background_color_component=content_background_cc)
        tracker_pane = ContentPane(bar_color_component=content_div_cc, background_color_component=content_background_cc)
        robot_state_pane = ContentPane(bar_color_component=content_div_cc, background_color_component=content_background_cc, size_hint=(1.5, 1))

        robot_state_image_pane = RobotImagePane(
            "./assets/robot.png",
            "./assets/pressurize.png",
            "./assets/pressurize_off.png",
            "./assets/depressurize.png",
            "./assets/depressurize_off.png",)

        # asm
        window.add_widget(main_layout)

        main_layout.add_widget(title)
        
        main_layout.add_widget(content_top)
        main_layout.add_widget(content_bottom)

        content_top.add_widget(controller_select_pane)
        content_top.add_widget(command_center_pane)

        content_bottom.add_widget(tracker_pane)
        content_bottom.add_widget(robot_state_pane)

        robot_state_pane.add_widget(robot_state_image_pane)

        robot_state_image_pane.actuator0.pressurize.add_callback(controls.pressurize0)
        robot_state_image_pane.actuator0.depressurize.add_callback(controls.depressurize0)

        robot_state_image_pane.actuator1.pressurize.add_callback(controls.pressurize1)
        robot_state_image_pane.actuator1.depressurize.add_callback(controls.depressurize1)

        robot_state_image_pane.actuator2.pressurize.add_callback(controls.pressurize2)
        robot_state_image_pane.actuator2.depressurize.add_callback(controls.depressurize2)

        robot_state_image_pane.actuator3.pressurize.add_callback(controls.pressurize3)
        robot_state_image_pane.actuator3.depressurize.add_callback(controls.depressurize3)

        robot_state_image_pane.actuator4.pressurize.add_callback(controls.pressurize4)
        robot_state_image_pane.actuator4.depressurize.add_callback(controls.depressurize4)

        robot_state_image_pane.actuator5.pressurize.add_callback(controls.pressurize5)
        robot_state_image_pane.actuator5.depressurize.add_callback(controls.depressurize5)

        for i in range(6):
            robot_state_image_pane.show_pressure(i, 100.4)

        Clock.schedule_interval(self._background_tasks, 1/100)
        return window

    def _background_tasks(self, dt):
        pass



if __name__ == '__main__':
    MainWindow().run()
