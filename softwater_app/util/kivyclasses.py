from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
from kivy.graphics import Rectangle
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.animation import Animation

import cv2
import numpy as np


class RobotImageBoxButtons(BoxLayout):
    def __init__(self, p_img, p_off_img, dp_img, dp_off_img):
        super(RobotImageBoxButtons, self).__init__()

        self.size_hint=(None, None)
        self.orientation = "horizontal"

        self.pressurize = IconButton(p_off_img, p_img, size_hint=(None, 1), pos_hint={"left": 1, "center_y": 0.5}, sticky=True)
        self.pressure = Label(text="N/A", size_hint=(None, 1), pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.depressurize = IconButton(dp_off_img, dp_img, size_hint=(None, 1), pos_hint={"right": 1, "center_y": 0.5}, sticky=True)

        self.pressurize_pressed = False
        self.depressurize_pressed = False

        self.pressurize.add_callback(self._pressurize_pressed)
        self.depressurize.add_callback(self._depressurize_pressed)

        self.add_widget(self.pressurize)
        self.add_widget(self.pressure)
        self.add_widget(self.depressurize)
    
    def on_size(self, *args):
        self.pressurize.width = self.size[1]
        self.pressure.width = self.size[0] - 2 * self.size[1]
        self.pressure.font_size = self.size[1] / 2.5
        self.depressurize.width = self.size[1]
    
    def _pressurize_pressed(self, pressed):
        self.pressurize_pressed = pressed
        if (self._exclusive_check()):
            self.depressurize.on_press()
    
    def _depressurize_pressed(self, pressed):
        self.depressurize_pressed = pressed
        if (self._exclusive_check()):
            self.pressurize.on_press()
    
    def _exclusive_check(self):
        if (self.pressurize_pressed):
            return self.depressurize_pressed
        elif (self.depressurize_pressed):
            return self.pressurize_pressed
        return False


class RobotImagePane(BoxLayout):
    def __init__(self, robot_image, pump_img, pump_off_img, gate_img, gate_off_img, p_img, p_off_img, dp_img, dp_off_img, size_hint=(1, 1), pos_hint={"x": 0, "y": 0}):
        super(RobotImagePane, self).__init__()
        self.size_hint = size_hint
        self.pos_hint = pos_hint

        self.main_button_layout = BoxLayout(size_hint=(0.3, None), orientation="vertical", pos_hint={"x": 0, "center_y": 0.5}, padding=10)
        self.robot_layout = FloatLayout()

        self.robot_image = ImagePane(robot_image)

        self.pump = IconButton(pump_off_img, pump_img, sticky=True, pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.gate = IconButton(gate_off_img, gate_img, sticky=True, pos_hint={"center_x": 0.5, "center_y": 0.5})

        self.actuator0 = RobotImageBoxButtons(p_img, p_off_img, dp_img, dp_off_img)
        self.actuator1 = RobotImageBoxButtons(p_img, p_off_img, dp_img, dp_off_img)
        self.actuator2 = RobotImageBoxButtons(p_img, p_off_img, dp_img, dp_off_img)
        self.actuator3 = RobotImageBoxButtons(p_img, p_off_img, dp_img, dp_off_img)
        self.actuator4 = RobotImageBoxButtons(p_img, p_off_img, dp_img, dp_off_img)
        self.actuator5 = RobotImageBoxButtons(p_img, p_off_img, dp_img, dp_off_img)

        self.add_widget(self.main_button_layout)
        self.add_widget(self.robot_layout)

        self.main_button_layout.add_widget(self.pump)
        self.main_button_layout.add_widget(self.gate)

        self.robot_layout.add_widget(self.robot_image)
        self.robot_layout.add_widget(self.actuator0)
        self.robot_layout.add_widget(self.actuator1)
        self.robot_layout.add_widget(self.actuator2)
        self.robot_layout.add_widget(self.actuator3)
        self.robot_layout.add_widget(self.actuator4)
        self.robot_layout.add_widget(self.actuator5)

        self.robot_layout.bind(size=self.image_button_layout, pos=self.image_button_layout)
        
    def image_button_layout(self, *args):
        col1 = 0.2575
        col2 = 0.5475
        col3 = 0.8375
        
        row1 = 0.79
        row2 = 0.20

        self.robot_image.size = self.robot_layout.size

        sx, sy = self.robot_image.image.norm_image_size
        px, py = (self.robot_layout.pos[0] + (self.robot_layout.size[0] - sx) / 2, self.robot_layout.pos[1] + (self.robot_layout.size[1] - sy) / 2)

        actuator_size = (0.235 * sx, 0.08 * sx)

        self.actuator0.size = actuator_size
        self.actuator0.center = (px + col1 * sx, py + row1 * sy)

        self.actuator1.size = actuator_size
        self.actuator1.center = (px + col1 * sx, py + row2 * sy)
        
        self.actuator2.size = actuator_size
        self.actuator2.center = (px + col2 * sx, py + row1 * sy)

        self.actuator3.size = actuator_size
        self.actuator3.center = (px + col2 * sx, py + row2 * sy)

        self.actuator4.size = actuator_size
        self.actuator4.center = (px + col3 * sx, py + row1 * sy)

        self.actuator5.size = actuator_size
        self.actuator5.center = (px + col3 * sx, py + row2 * sy)
    
    def show_pressure(self, actuator, pressure):
        text = f"{pressure:.1f}"

        if (actuator == 0):
            self.actuator0.pressure.text = text
        elif (actuator == 1):
            self.actuator1.pressure.text = text
        elif (actuator == 2):
            self.actuator2.pressure.text = text
        elif (actuator == 3):
            self.actuator3.pressure.text = text
        elif (actuator == 4):
            self.actuator4.pressure.text = text
        elif (actuator == 5):
            self.actuator5.pressure.text = text
        


class ContentPane(FloatLayout):
    def __init__(self, size_hint=(1, 1), pos_hint={}, bar_color_component=None, background_color_component=None):
        super(ContentPane, self).__init__()
        self.size_hint = size_hint
        self.pos_hint = pos_hint
        self.background_color_component = background_color_component

        if background_color_component is not None:
            with self.canvas:
                self._rect = Rectangle(texture=background_color_component.texture)

        if bar_color_component is not None:
            self.div = Divider(size_hint=(1, None), height=10, pos_hint={'x': 0, 'top': 1}, color_component=bar_color_component)
            self.add_widget(self.div)
        
        self.bind(size=self.update, pos=self.update)
    
    def update(self, *args):
        if self.background_color_component is not None:
            self._rect.size = self.size
            self._rect.pos = self.pos


class MainContentPane(FloatLayout):
    def __init__(self, title_image, background_image, size_hint=(1, 1), pos_hint={}):
        super(MainContentPane, self).__init__()
        self.background_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)
        self.size_hint = size_hint
        self.pos_hint = pos_hint
        
        self.add_widget(self.background_image)
        
    def on_size(self, *args):
        self.background_image.size = self.size


class ImagePane(FloatLayout):
    def __init__(self, image_source, size_hint=(1, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5}, width=None, height=None):
        super(ImagePane, self).__init__()
        self.size_hint = size_hint
        self.pos_hint = pos_hint
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height

        with self.canvas:
            self.image = Image(source=image_source)
        self.bind(size=self.update, pos=self.update)

    def update(self, *args):
        self.image.size = self.size
        self.image.pos = self.pos


class CV2ImagePane(FloatLayout):
    def __init__(self, size_hint=(1, 1), pos_hint={}):
        super(CV2ImagePane, self).__init__()
        self.size_hint = size_hint
        self.pos_hint = pos_hint

        self._image = CV2Image(pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.add_widget(self._image)

    def set_image(self, img):
        self._image.set_image(img)


class CV2Image(Image):
    def __init__(self, size_hint=(1, 1), pos_hint={}):
        super(CV2Image, self).__init__()
        self.size_hint = size_hint
        self.pos_hint = pos_hint

    def set_image(self, img):
        new_size = [int(self.size[0]), int(img.shape[0] * (self.size[0] / img.shape[1]))]
        img = cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)
        img = cv2.flip(img, 0)
        img = np.uint8(img * 255)
        buf = img.tobytes()
        texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.texture = texture


class IconButton(ButtonBehavior, Widget):
    def __init__(self, icon_normal, icon_pressed, size_hint=(1, 1), pos_hint={}, sticky=False):
        super(IconButton, self).__init__()
        self._icon_normal = Image(source=icon_normal)
        self._icon_pressed = Image(source=icon_pressed)
        self._icon_pressed.opacity = 0
        self.size_hint = size_hint
        self.pos_hint = pos_hint
        self.sticky = sticky

        self.always_release = True
        self._callbacks = []
        self.pressed = False
        self.mouse_pos = (0, 0)

        self.return_time = 0.2
        self.react_time = 0.1

        self._return_anim = Animation(opacity=1, duration=self.return_time)

        self.add_widget(self._icon_normal)
        self.add_widget(self._icon_pressed)
        self.bind(size=self.update, pos=self.update)
        Window.bind(mouse_pos=self.on_mousepos)

    def add_callback(self, func):
        self._callbacks.append(func)
    
    def on_mousepos(self, window, pos):
        self.mouse_pos = pos

    def on_press(self):
        if self.pressed:
            if not self._collide_check(self._icon_pressed):
                return
        else:
            if not self._collide_check(self._icon_normal):
                return

        fadein = Animation(opacity=1, duration=self.react_time)
        fadeout = Animation(opacity=0, duration=self.react_time)

        if self.sticky and self.pressed:
            fadein.start(self._icon_normal)
            fadeout.start(self._icon_pressed)
            self.pressed = False
        else:
            fadein.start(self._icon_pressed)
            fadeout.start(self._icon_normal)
            self.pressed = True
                
        for func in self._callbacks:
                func(self.pressed)
    
    def _collide_check(self, image):
        size = image.norm_image_size
        pos = (image.pos[0] + (image.size[0] - size[0]) / 2, image.pos[1] + (image.size[1] - size[1]) / 2)

        if self.mouse_pos[0] >= pos[0] and self.mouse_pos[0] <= pos[0] + size[0] and self.mouse_pos[1] >= pos[1] and self.mouse_pos[1] <= pos[1] + size[1]:
            return True
        return False


    def on_release(self):
        if not self.sticky:
            self.pressed = False
            
            fadein = Animation(opacity=1, duration=self.react_time)
            fadeout = Animation(opacity=0, duration=self.react_time)

            fadein.start(self._icon_normal)
            fadeout.start(self._icon_pressed)
            for func in self._callbacks:
                func(self.pressed)

    def update(self, *args):
        self._icon_pressed.size = self.size
        self._icon_pressed.pos = self.pos
        self._icon_normal.size = self.size
        self._icon_normal.pos = self.pos        


class Divider(Widget):
    def __init__(self, width=100, height=100, size_hint=(1, 1), pos_hint={}, color_component=None, rotate_speed=None):
        super(Divider, self).__init__()
        self.width = width
        self.height = height
        self.size_hint = size_hint
        self.pos_hint = pos_hint

        self.color_component = color_component
        self._rotate_speed = rotate_speed

        if color_component is not None:
            with self.canvas:
                self._rect = Rectangle(pos=self.pos, size=self.size, texture=color_component.texture)
            if rotate_speed is not None:
                Clock.schedule_interval(self._color_callback, 1/10)
        else:
            self._rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(size=self.update, pos=self.update)

    def _color_callback(self, dt):
        self.color_component.rotate(self._rotate_speed)
        self._rect.texture = self.color_component.texture

    def update(self, *args):
        self._rect.size = self.size
        self._rect.pos = self.pos
