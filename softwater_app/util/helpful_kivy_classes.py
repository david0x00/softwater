from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior, ToggleButtonBehavior
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
from kivy.graphics import Rectangle, RoundedRectangle
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.animation import Animation

import cv2
import numpy as np

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


class CV2Image(Image):
    def __init__(self, size_hint=(1, 1), pos_hint={}):
        super(CV2Image, self).__init__()
        self.size_hint = size_hint
        self.pos_hint = pos_hint

        self.img_size = (0, 0)

        self.cv2_img = None
        self.zoom = ((0, 0), (1, 1))
    
    def set_zoom(self, zoom):
        self.zoom = zoom
        self._redo_texture()

    def set_image(self, img):
        self.cv2_img = img
        self._redo_texture()
    
    def reset_zoom(self):
        self.zoom = ((0, 0), (1, 1))
    
    def _redo_texture(self):
        if self.cv2_img is None:
            return
        
        w = self.cv2_img.shape[1]
        h = self.cv2_img.shape[0]

        x1 = self.zoom[0][0]
        y1 = self.zoom[0][1]
        x2 = self.zoom[1][0]
        y2 = self.zoom[1][1]

        x = int(x1 * w)
        y = int(y1 * h)

        dx = int(x2 * w) - x
        dy = int(y2 * h) - y

        if dx <= 0:
            dx = 1
        if dy <= 0:
            dy = 1

        crop = self.cv2_img[y:(y + dy), x:(x + dx)]

        img_size = [int(self.size[0]), int(crop.shape[0] * (self.size[0] / crop.shape[1]))]
        if (img_size[1] > self.size[1]):
            img_size[0] = int(img_size[0] * self.size[1] / float(img_size[1]))
            img_size[1] = int(self.size[1])
        
        self.img_size = img_size

        print(crop.shape)

        img = cv2.resize(crop, self.img_size, interpolation=cv2.INTER_AREA)
        img = cv2.flip(img, 0)
        img = np.uint8(img)
        buf = img.tobytes()
        texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.texture = texture



class RoundToggleButton(ToggleButtonBehavior, FloatLayout):
    def __init__(self, text_down, text_up, cc_down, cc_up, text_size=0.3, radius=10):
        super(RoundToggleButton, self).__init__()
        self.text_down = text_down
        self.text_up = text_up
        self.cc_down = cc_down
        self.cc_up = cc_up
        self.radius = [radius]
        self.text_size = text_size

        self._callbacks = []

        with self.canvas:
            self.rect = RoundedRectangle(radius=self.radius, texture=cc_up.texture)
        
        self.label = Label(text=text_up)

        self.add_widget(self.label)

        self.bind(size=self.update, pos=self.update)

    def add_callback(self, func):
        self._callbacks.append(func)

    def on_state(self, widget, value):
        pressed = value == "down"
        if pressed:
            self.rect.texture = self.cc_down.texture
            self.label.text = self.text_down
        else:
            self.rect.texture = self.cc_up.texture
            self.label.text = self.text_up
        
        for func in self._callbacks:
            func(pressed)

    def update(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
        self.label.size = self.size
        self.label.pos = self.pos
        self.label.font_size = self.size[1] * self.text_size


class IconButton(ButtonBehavior, FloatLayout):
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

        self.return_time = 0.2
        self.react_time = 0.1

        self._return_anim = Animation(opacity=1, duration=self.return_time)

        self.add_widget(self._icon_normal)
        self.add_widget(self._icon_pressed)
        self.bind(size=self.update, pos=self.update)

    def add_callback(self, func):
        self._callbacks.append(func)

    def on_press(self):
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
