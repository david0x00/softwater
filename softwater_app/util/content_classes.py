from kivy.clock import Clock
from util.helpful_kivy_classes import *
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
import cv2
import numpy as np


class CommandCenter(BoxLayout):
    def __init__(self, button_up_cc, button_down_cc, size_hint=(1, 1), pos_hint={"center_x": 0.5, "center_y": 0.5}):
        super(CommandCenter, self).__init__()
        self.size_hint = size_hint
        self.pos_hint = pos_hint
        self.padding = 20
        self.spacing = 10
        self.orientation = "vertical"

        layout1 = BoxLayout(orientation="horizontal", spacing=40)
        layout3 = BoxLayout(orientation="horizontal", spacing=40)
        layout4 = BoxLayout(orientation="horizontal", spacing=40)

        robot_status_title_label = ResizableLabel("Robot Status:", 0.4, halign="left")
        self.robot_status_label = ResizableLabel("Not Connected", 0.4)
        self.robot_status_ping = ResizableLabel("", 0.4, halign="right")
        self.log_button = RoundToggleButton("Log", "Log", button_down_cc, button_up_cc)

        self.start_button = RoundToggleButton("Start", "Start", button_down_cc, button_up_cc)
        self.stop_button = RoundToggleButton("Stop", "Stop", button_down_cc, button_up_cc)

        self.add_widget(layout1)
        self.add_widget(self.log_button)
        self.add_widget(layout3)
        self.add_widget(layout4)

        layout3_1 = BoxLayout(orientation="horizontal")
        layout3_2 = BoxLayout(orientation="horizontal")

        self.frequency_text = ResizableTextInput("", 0.4, size_hint=(1, 0.8), input_filter="float")
        self.duration_text = ResizableTextInput("", 0.4, size_hint=(1, 0.8), input_filter="float")

        layout3_1.add_widget(ResizableLabel("Frequency:", 0.3, size_hint=(0.9, 1)))
        layout3_1.add_widget(self.frequency_text)
        layout3_1.add_widget(ResizableLabel("Hz", 0.3, size_hint=(0.5, 1)))
        
        layout3_2.add_widget(ResizableLabel("Duration:", 0.3, size_hint=(0.7, 1)))
        layout3_2.add_widget(self.duration_text)
        layout3_2.add_widget(ResizableLabel("sec", 0.3, size_hint=(0.5, 1)))

        layout1.add_widget(robot_status_title_label)
        layout1.add_widget(self.robot_status_label)
        layout1.add_widget(self.robot_status_ping)
        layout3.add_widget(layout3_1)
        layout3.add_widget(layout3_2)
        
        layout4.add_widget(self.start_button)
        layout4.add_widget(self.stop_button)

        self.start_button.add_callback(self._start_pressed)
        self.stop_button.add_callback(self._stop_presssed)
    
    def set_robot_status(self, connected, ping):
        if connected:
            self.robot_status_label.text = "Connected"
            self.robot_status_label.color = "#00FF00"
        else:
            self.robot_status_label.text = "Not Connected"
            self.robot_status_label.color = "#FF0000"
        self.robot_status_ping.text = ping
    
    def _start_pressed(self, pressed):
        if (pressed):
            self.stop_button.state = "normal"

    def _stop_presssed(self, pressed):
        if (pressed):
            self.start_button.state = "normal"


class ControlSelector(GridLayout):
    def __init__(self, button_up_cc, button_down_cc, size_hint=(1, 1), pos_hint={"center_x": 0.5, "center_y": 0.5}):
        super(ControlSelector, self).__init__()
        self.size_hint = size_hint
        self.pos_hint = pos_hint
        self.padding = 20
        self.spacing = 10
        self.cols = 3
        self.rows = 2

        self.auto_mpc_button = RoundToggleButton("Auto MPC", "Auto MPC", button_down_cc, button_up_cc)
        self.pid_button = RoundToggleButton("Visual Servo", "Visual Servo", button_down_cc, button_up_cc)
        self.open_loop_button = RoundToggleButton("Open Loop", "Open Loop", button_down_cc, button_up_cc)
        self.manual_button = RoundToggleButton("Manual", "Manual", button_down_cc, button_up_cc)

        self.target_text = ResizableLabel("Target IDX:", 0.25)
        target_layout = BoxLayout(orientation='horizontal')
        self.target = ResizableTextInput("", 0.25)
        self.target_coords = ResizableLabel("N/A", 0.25)

        self.add_widget(self.auto_mpc_button)
        self.add_widget(self.pid_button)
        self.add_widget(self.target_text)
        self.add_widget(self.open_loop_button)
        self.add_widget(self.manual_button)
        self.add_widget(target_layout)

        target_layout.add_widget(self.target)
        target_layout.add_widget(self.target_coords)

        self.auto_mpc_button.add_callback(self._auto_mpc_pressed)
        self.pid_button.add_callback(self._pid_pressed)
        self.open_loop_button.add_callback(self._open_loop_pressed)
        self.manual_button.add_callback(self._manual_pressed)
    
    def _auto_mpc_pressed(self, pressed):
        if (pressed):
            self.pid_button.state = "normal"
            self.open_loop_button.state = "normal"
            self.manual_button.state = "normal"
    
    def _pid_pressed(self, pressed):
        if (pressed):
            self.auto_mpc_button.state = "normal"
            self.open_loop_button.state = "normal"
            self.manual_button.state = "normal"

    def _open_loop_pressed(self, pressed):
        if (pressed):
            self.auto_mpc_button.state = "normal"
            self.pid_button.state = "normal"
            self.manual_button.state = "normal"

    def _manual_pressed(self, pressed):
        if (pressed):
            self.auto_mpc_button.state = "normal"
            self.pid_button.state = "normal"
            self.open_loop_button.state = "normal"

class SettingsPane(ScrollView):
    def __init__(self, size_hint=(1, 1), pos_hint={"center_x": 0.5, "center_y": 0.5}):
        super(SettingsPane, self).__init__()
        self.size_hint = size_hint
        self.pos_hint = pos_hint
        
        self.layout = BoxLayout(orientation="vertical", size_hint=(1, None), height=600, spacing=10, padding=10)

        camera_settings_header = ResizableLabel("Camera Settings", 0.75, size_hint=(1, 2))
        self.brightness = TextNumberSlider("Brightness", 0.8, 0, 100, 0, pos_hint={"x": 0})
        self.contrast = TextNumberSlider("Contrast", 0.8, 0, 100, 0, pos_hint={"x": 0})
        self.saturation = TextNumberSlider("Saturation", 0.8, 0, 100, 0, pos_hint={"x": 0})

        r = 0.6
        tracker_settings_header = ResizableLabel("Tracker Settings", 0.75, size_hint=(1, 2))

        layout1 = BoxLayout(orientation="horizontal")
        self.hue_avg = ResizableTextInput("", r)
        self.hue_error = ResizableTextInput("", r)

        layout1.add_widget(ResizableLabel("Hue:", r, size_hint=(1.5, 1), halign="left"))
        layout1.add_widget(ResizableLabel("Avg:", r))
        layout1.add_widget(self.hue_avg)
        layout1.add_widget(ResizableLabel("Error:", r))
        layout1.add_widget(self.hue_error)

        layout2 = BoxLayout(orientation="horizontal")
        self.saturation_low = ResizableTextInput("", r)
        self.saturation_high = ResizableTextInput("", r)
        layout2.add_widget(ResizableLabel("Saturation:", r, size_hint=(1.5, 1), halign="left"))
        layout2.add_widget(ResizableLabel("Low:", r))
        layout2.add_widget(self.saturation_low)
        layout2.add_widget(ResizableLabel("High:", r))
        layout2.add_widget(self.saturation_high)

        layout3 = BoxLayout(orientation="horizontal")
        self.value_low = ResizableTextInput("", r)
        self.value_high = ResizableTextInput("", r)
        layout3.add_widget(ResizableLabel("Value:", r, size_hint=(1.5, 1), halign="left"))
        layout3.add_widget(ResizableLabel("Low:", r))
        layout3.add_widget(self.value_low)
        layout3.add_widget(ResizableLabel("High:", r))
        layout3.add_widget(self.value_high)

        layout4 = BoxLayout(orientation="horizontal")
        self.gaussian_blur_x = ResizableTextInput("", r)
        self.gaussian_blur_y = ResizableTextInput("", r)
        layout4.add_widget(ResizableLabel("Gaussian Blur:", r, size_hint=(1.5, 1), halign="left"))
        layout4.add_widget(ResizableLabel("x:", r))
        layout4.add_widget(self.gaussian_blur_x)
        layout4.add_widget(ResizableLabel("y:", r))
        layout4.add_widget(self.gaussian_blur_y)

        layout5 = BoxLayout(orientation="horizontal")
        self.circularity_min = ResizableTextInput("", r)
        self.circularity_max = ResizableTextInput("", r)
        layout5.add_widget(ResizableLabel("Circularity:", r, size_hint=(1.5, 1), halign="left"))
        layout5.add_widget(ResizableLabel("Min:", r))
        layout5.add_widget(self.circularity_min)
        layout5.add_widget(ResizableLabel("Max:", r))
        layout5.add_widget(self.circularity_max)

        layout6 = BoxLayout(orientation="horizontal")
        self.area_min = ResizableTextInput("", r)
        self.area_max = ResizableTextInput("", r)
        layout6.add_widget(ResizableLabel("Area:", r, size_hint=(1.5, 1), halign="left"))
        layout6.add_widget(ResizableLabel("Min:", r))
        layout6.add_widget(self.area_min)
        layout6.add_widget(ResizableLabel("Max:", r))
        layout6.add_widget(self.area_max)

        layout7 = BoxLayout(orientation="horizontal")
        self.inertia_min = ResizableTextInput("", r)
        self.inertia_max = ResizableTextInput("", r)
        layout7.add_widget(ResizableLabel("Inertia:", r, size_hint=(1.5, 1), halign="left"))
        layout7.add_widget(ResizableLabel("Min:", r))
        layout7.add_widget(self.inertia_min)
        layout7.add_widget(ResizableLabel("Max:", r))
        layout7.add_widget(self.inertia_max)

        self.add_widget(self.layout)

        self.layout.add_widget(camera_settings_header)
        self.layout.add_widget(self.brightness)
        self.layout.add_widget(self.contrast)
        self.layout.add_widget(self.saturation)

        self.layout.add_widget(tracker_settings_header)
        self.layout.add_widget(layout1)
        self.layout.add_widget(layout2)
        self.layout.add_widget(layout3)
        self.layout.add_widget(layout4)
        self.layout.add_widget(layout5)
        self.layout.add_widget(layout6)
        self.layout.add_widget(layout7)


class CameraImageSelector(CV2Image, FloatLayout):
    def __init__(self, cc, size_hint=(1, 1), pos_hint={}):
        super(CameraImageSelector, self).__init__()
        self.size_hint = size_hint
        self.pos_hint = pos_hint

        self.rect = Divider(size_hint=(None, None), color_component=cc)
        self.rect.opacity = 0

        self.selecting = False
        self.mouse_pos = None

        self.add_widget(self.rect)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        if self.collide_point(*pos) and self._inbounds(pos):
            self.mouse_pos = pos
        else:
            self.mouse_pos = None
    
    def get_hsv(self):
        if self.cv2_img is None:
            return None
        
        w = float(self.img_size[0])
        h = float(self.img_size[1])

        if w <= 0 or h <= 0 or self.mouse_pos is None:
            return None
    
        pos = (self.pos[0] + (self.size[0] - w) / 2, h + self.pos[1] + (self.size[1] - h) / 2)
        x = abs((self.mouse_pos[0] - pos[0]) / w)
        y = abs((self.mouse_pos[1] - pos[1]) / h)

        zx1 = self.zoom[0][0]
        zy1 = self.zoom[0][1]
        zx2 = self.zoom[1][0]
        zy2 = self.zoom[1][1]

        x = int((zx1 + x * (zx2 - zx1)) * self.cv2_img.shape[1])
        y = int((zy1 + y * (zy2 - zy1)) * self.cv2_img.shape[0])

        if x >= self.cv2_img.shape[1] or y >= self.cv2_img.shape[0]:
            return None

        bgr = self.cv2_img[y, x]
        pxl = np.zeros((1, 1, 3), dtype=np.uint8)
        pxl[0, 0] = bgr
        hsv = cv2.cvtColor(pxl, cv2.COLOR_BGR2HSV)
        return hsv[0, 0]

    def on_touch_up(self, touch):
        if (self.selecting):
            self.rect.opacity = 0
            self.selecting = False
            bw, bh = self._forcebounds(touch.pos)
            
            w = float(self.img_size[0])
            h = float(self.img_size[1])

            if (bw == 0 or bh == 0):
                return

            pos = (self.pos[0] + (self.size[0] - w) / 2, h + self.pos[1] + (self.size[1] - h) / 2)

            if (bw < 0):
                x1 = self.rect.pos[0] + bw
                x2 = self.rect.pos[0]
            else:
                x1 = self.rect.pos[0]
                x2 = self.rect.pos[0] + bw
            
            if (bh < 0):
                y1 = self.rect.pos[1]
                y2 = self.rect.pos[1] + bh
            else:
                y1 = self.rect.pos[1] + bh
                y2 = self.rect.pos[1]

            x1 = abs(pos[0] - x1)
            y1 = abs(pos[1] - y1)
            x2 = abs(pos[0] - x2)
            y2 = abs(pos[1] - y2)

            zoom = [[x1 / w, y1 / h], [x2 / w, y2 / h]]

            zx1 = self.zoom[0][0]
            zy1 = self.zoom[0][1]
            zx2 = self.zoom[1][0]
            zy2 = self.zoom[1][1]

            zoom[0][0] = int((zx1 + zoom[0][0] * (zx2 - zx1)) * self.cv2_img.shape[1]) / float(self.cv2_img.shape[1])
            zoom[0][1] = int((zy1 + zoom[0][1] * (zy2 - zy1)) * self.cv2_img.shape[0]) / float(self.cv2_img.shape[0])
            zoom[1][0] = int((zx1 + zoom[1][0] * (zx2 - zx1)) * self.cv2_img.shape[1]) / float(self.cv2_img.shape[1])
            zoom[1][1] = int((zy1 + zoom[1][1] * (zy2 - zy1)) * self.cv2_img.shape[0]) / float(self.cv2_img.shape[0])

            self.set_zoom(zoom)

    def on_touch_down(self, touch):
        if self._inbounds(touch.pos):
            self.rect.opacity = 0.4
            self.rect.pos = touch.pos
            self.rect.size = (0, 0)
            self.selecting = True

    def on_touch_move(self, touch):
        if (self.selecting):
            w, h = self._forcebounds(touch.pos)
            self.rect.width = w
            self.rect.height = h
        
    def _inbounds(self, pos):
        _pos = (self.pos[0] + (self.size[0] - self.img_size[0]) / 2, self.pos[1] + (self.size[1] - self.img_size[1]) / 2)
        return pos[0] >= _pos[0] and pos[0] <= _pos[0] + self.img_size[0] and pos[1] >= _pos[1] and pos[1] <= _pos[1] + self.img_size[1]
    
    def _forcebounds(self, pos):
        _pos = (self.pos[0] + (self.size[0] - self.img_size[0]) / 2, self.pos[1] + (self.size[1] - self.img_size[1]) / 2)
        w = pos[0] - self.rect.pos[0]
        h = pos[1] - self.rect.pos[1]
        if (self.rect.pos[0] + w <= _pos[0]):
            w = _pos[0] - self.rect.pos[0]
        elif (self.rect.pos[0] + w >= _pos[0] + self.img_size[0]):
            w = _pos[0] + self.img_size[0] - self.rect.pos[0]
        if (self.rect.pos[1] + h <= _pos[1]):
            h = _pos[1] - self.rect.pos[1]
        elif (self.rect.pos[1] + h >= _pos[1] + self.img_size[1]):
            h = _pos[1] + self.img_size[1] - self.rect.pos[1]
        return w, h


class CameraPane(BoxLayout):
    def __init__(self, button_up_cc, button_down_cc, select_cc, size_hint=(1, 1), pos_hint={"x": 0, "y": 0}):
        super(CameraPane, self).__init__()
        self.size_hint = size_hint
        self.pos_hint = pos_hint
        self.orientation = "horizontal"
        self.padding = 10
        self.spacing = 10

        self.button_layout = BoxLayout(orientation="vertical", size_hint=(0.35, 0.9), pos_hint={"x": 0, "center_y": 0.5}, spacing=10)
        self.image = CameraImageSelector(select_cc, size_hint=(1, 0.9), pos_hint={"center_x": 0.5, "center_y": 0.5})

        self.camera_view = RoundToggleButton("Camera", "Camera", button_down_cc, button_up_cc)
        self.tracker_view = RoundToggleButton("Tracker", "Tracker", button_down_cc, button_up_cc)
        self.reset_zoom = RoundToggleButton("Reset Zoom", "Reset Zoom", button_down_cc, button_up_cc)
        self.reset_detector = RoundToggleButton("Reset Detector", "Reset Detector", button_down_cc, button_up_cc)
        self.rgb_layout = BoxLayout(orientation="horizontal", size_hint=(1, 1))

        label_layout = BoxLayout(orientation="horizontal")
        detector_status_label = ResizableLabel("Detector Status:", 0.4, halign="left")
        self.detector_status = ResizableLabel("No Track", 0.4, halign="right", size_hint=(0.7, 1))

        self.r = ResizableLabel("H", 0.3)
        self.g = ResizableLabel("S", 0.3)
        self.b = ResizableLabel("V", 0.3)

        self.add_widget(self.button_layout)
        self.add_widget(self.image)

        self.button_layout.add_widget(self.camera_view)
        self.button_layout.add_widget(self.tracker_view)
        self.button_layout.add_widget(self.reset_zoom)
        self.button_layout.add_widget(self.reset_detector)
        self.button_layout.add_widget(label_layout)
        self.button_layout.add_widget(self.rgb_layout)

        label_layout.add_widget(detector_status_label)
        label_layout.add_widget(self.detector_status)

        self.rgb_layout.add_widget(self.r)
        self.rgb_layout.add_widget(self.g)
        self.rgb_layout.add_widget(self.b)

        self.camera_view.add_callback(self._camera_view_pressed)
        self.tracker_view.add_callback(self._tracker_view_pressed)
        self.reset_zoom.add_callback(self._reset_zoom_button_pressed)

        self.camera_view_pressed = True
        self.tracker_view_pressed = False

        self.camera_view.state = "down"

        self.bind(size=self.update, pos=self.update)
        Clock.schedule_interval(self._update_hsv, 1/4)
    
    def _camera_view_pressed(self, pressed):
        self.camera_view_pressed = pressed
        if (pressed):
            self.tracker_view.state = "normal"
        else:
            self.tracker_view.state = "down"
    
    def _tracker_view_pressed(self, pressed):
        self.tracker_view_pressed = pressed
        if (pressed):
            self.camera_view.state = "normal"
        else:
            self.camera_view.state = "down"
        
    def _reset_zoom_button_pressed(self, pressed):
        self.image.reset_zoom()
    
    def set_detector_status(self, tracking):
        if tracking:
            self.detector_status.text = "Tracking"
            self.detector_status.color = "#00FF00"
        else:
            self.detector_status.text = "No Track"
            self.detector_status.color = "#FF0000"
    
    def update(self, *args):
        self.r.font_size = self.r.size[1] / 2
        self.g.font_size = self.g.size[1] / 2
        self.b.font_size = self.b.size[1] / 2
    
    def _update_hsv(self, dt):
        rgb = self.image.get_hsv()
        if rgb is not None:
            self.r.text = str(int(float(str(rgb[0]))))
            self.g.text = str(int(float(str(rgb[1]))))
            self.b.text = str(int(float(str(rgb[2]))))
        else:
            self.r.text = "H"
            self.g.text = "S"
            self.b.text = "V"

class RobotImageBoxButtons(BoxLayout):
    def __init__(self, id, p_img, p_off_img, dp_img, dp_off_img):
        super(RobotImageBoxButtons, self).__init__()

        self.id = id

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

        self._pressurize_callbacks = []
        self._depressurize_callbacks = []
    
    def on_size(self, *args):
        self.pressurize.width = self.size[1]
        self.pressure.width = self.size[0] - 2 * self.size[1]
        self.pressure.font_size = self.size[1] / 2.5
        self.depressurize.width = self.size[1]

    def add_pressurize_callback(self, func):
        self._pressurize_callbacks.append(func)
    
    def add_depressurize_callback(self, func):
        self._depressurize_callbacks.append(func)
    
    def _pressurize_pressed(self, pressed):
        self.pressurize_pressed = pressed
        if (self._exclusive_check()):
            self.depressurize.on_press()
        for func in self._pressurize_callbacks:
            func(self.id, pressed)
    
    def _depressurize_pressed(self, pressed):
        self.depressurize_pressed = pressed
        if (self._exclusive_check()):
            self.pressurize.on_press()
        for func in self._depressurize_callbacks:
            func(self.id, pressed)
    
    def _exclusive_check(self):
        return self.pressurize_pressed and self.depressurize_pressed


class RobotImagePane(BoxLayout):
    def __init__(self, robot_image, button_up_cc, button_down_cc, p_img, p_off_img, dp_img, dp_off_img, size_hint=(1, 1), pos_hint={"x": 0, "y": 0}):
        super(RobotImagePane, self).__init__()
        self.size_hint = size_hint
        self.pos_hint = pos_hint
        self.orientation = "horizontal"
        self.padding = 10

        self.button_layout = BoxLayout(orientation="vertical", size_hint=(0.25, 0.5), pos_hint={"x": 0, "center_y": 0.5}, spacing=10)
        self.robot_layout = FloatLayout()

        self.robot_image = ImagePane(robot_image)

        self.pump = RoundToggleButton("Pump", "Pump", button_down_cc, button_up_cc)
        self.gate = RoundToggleButton("Gate", "Gate", button_down_cc, button_up_cc)

        self.actuator0 = RobotImageBoxButtons(0, p_img, p_off_img, dp_img, dp_off_img)
        self.actuator1 = RobotImageBoxButtons(1, p_img, p_off_img, dp_img, dp_off_img)
        self.actuator2 = RobotImageBoxButtons(2, p_img, p_off_img, dp_img, dp_off_img)
        self.actuator3 = RobotImageBoxButtons(3, p_img, p_off_img, dp_img, dp_off_img)
        self.actuator4 = RobotImageBoxButtons(4, p_img, p_off_img, dp_img, dp_off_img)
        self.actuator5 = RobotImageBoxButtons(5, p_img, p_off_img, dp_img, dp_off_img)

        self.add_widget(self.button_layout)
        self.add_widget(self.robot_layout)

        self.button_layout.add_widget(self.pump)
        self.button_layout.add_widget(self.gate)

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
