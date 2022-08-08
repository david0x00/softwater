from turtle import pos
from kivy.clock import Clock
from util.helpful_kivy_classes import *


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
        robot_status_label = ResizableLabel("Not Connected", 0.4, halign="right")
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
        layout1.add_widget(robot_status_label)
        layout3.add_widget(layout3_1)
        layout3.add_widget(layout3_2)
        
        layout4.add_widget(self.start_button)
        layout4.add_widget(self.stop_button)

        self.start_button.add_callback(self._start_pressed)
        self.stop_button.add_callback(self._stop_presssed)
    
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
        self.cols = 2
        self.rows = 4

        self.auto_mpc_button = RoundToggleButton("Auto MPC", "Auto MPC", button_down_cc, button_up_cc, size_hint=(0.2, 1))
        self.pid_button = RoundToggleButton("PID", "PID", button_down_cc, button_up_cc, size_hint=(0.2, 1))
        self.open_loop_button = RoundToggleButton("Open Loop", "Open Loop", button_down_cc, button_up_cc, size_hint=(0.2, 1))
        self.manual_button = RoundToggleButton("Manual", "Manual", button_down_cc, button_up_cc, size_hint=(0.2, 1))
    
        auto_mpc_selector = FileSelector(button_up_cc, button_down_cc)
        pid_selector = FileSelector(button_up_cc, button_down_cc)
        open_loop_selector = FileSelector(button_up_cc, button_down_cc)

        self.add_widget(self.auto_mpc_button)
        self.add_widget(auto_mpc_selector)
        self.add_widget(self.pid_button)
        self.add_widget(pid_selector)
        self.add_widget(self.open_loop_button)
        self.add_widget(open_loop_selector)
        self.add_widget(self.manual_button)

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

class SettingsPane(BoxLayout):
    def __init__(self, size_hint=(1, 1), pos_hint={"center_x": 0.5, "center_y": 0.5}):
        super(SettingsPane, self).__init__()
        self.size_hint = size_hint
        self.pos_hint = pos_hint
        self.orientation = "vertical"
        self.padding = 10
        self.spacing = 10

        camera_settings_header = ResizableLabel("Camera Settings", 0.75, size_hint=(1, 2))
        self.brightness = TextNumberSlider("Brightness", 1, 0, 100, 0, pos_hint={"x": 0})
        self.contrast = TextNumberSlider("Contrast", 1, 0, 100, 0, pos_hint={"x": 0})
        self.saturation = TextNumberSlider("Saturation", 1, 0, 100, 0, pos_hint={"x": 0})
        self.exposure = TextNumberSlider("Exposure", 1, -7, -1, -7, pos_hint={"x": 0})

        tracker_settings_header = ResizableLabel("Tracker Settings", 0.75, size_hint=(1, 2))
        self.r_min = TextNumberSlider("R Min", 1, 0, 255, 0, pos_hint={"x": 0})
        self.r_max = TextNumberSlider("R Max", 1, 0, 255, 0, pos_hint={"x": 0})
        self.g_min = TextNumberSlider("G Min", 1, 0, 255, 0, pos_hint={"x": 0})
        self.g_max = TextNumberSlider("G Max", 1, 0, 255, 0, pos_hint={"x": 0})
        self.b_min = TextNumberSlider("B Min", 1, 0, 255, 0, pos_hint={"x": 0})
        self.b_max = TextNumberSlider("B Max", 1, 0, 255, 0, pos_hint={"x": 0})

        self.add_widget(camera_settings_header)
        self.add_widget(self.brightness)
        self.add_widget(self.contrast)
        self.add_widget(self.saturation)
        self.add_widget(self.exposure)

        self.add_widget(tracker_settings_header)
        self.add_widget(self.r_min)
        self.add_widget(self.r_max)
        self.add_widget(self.g_min)
        self.add_widget(self.g_max)
        self.add_widget(self.b_min)
        self.add_widget(self.b_max)


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
    
    def get_rgb(self):
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
        return (bgr[2], bgr[1], bgr[0])

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
        self.reset = RoundToggleButton("Reset", "Reset", button_down_cc, button_up_cc)
        self.rgb_layout = BoxLayout(orientation="horizontal", size_hint=(1, 1))
        self.r = ResizableLabel("R", 0.3)
        self.g = ResizableLabel("G", 0.3)
        self.b = ResizableLabel("B", 0.3)

        self.add_widget(self.button_layout)
        self.add_widget(self.image)

        self.button_layout.add_widget(self.camera_view)
        self.button_layout.add_widget(self.tracker_view)
        self.button_layout.add_widget(self.reset)
        self.button_layout.add_widget(self.rgb_layout)

        self.rgb_layout.add_widget(self.r)
        self.rgb_layout.add_widget(self.g)
        self.rgb_layout.add_widget(self.b)

        self.camera_view.add_callback(self._camera_view_pressed)
        self.tracker_view.add_callback(self._tracker_view_pressed)
        self.reset.add_callback(self._reset_button_pressed)

        self.camera_view_pressed = True
        self.tracker_view_pressed = False

        self.camera_view.state = "down"

        self.bind(size=self.update, pos=self.update)
        Clock.schedule_interval(self._update_rgb, 1/4)
    
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
        
    def _reset_button_pressed(self, pressed):
        self.image.reset_zoom()
    
    def update(self, *args):
        self.r.font_size = self.r.size[1] / 2
        self.g.font_size = self.g.size[1] / 2
        self.b.font_size = self.b.size[1] / 2
    
    def _update_rgb(self, dt):
        rgb = self.image.get_rgb()
        if rgb is not None:
            self.r.text = str(rgb[0])
            self.g.text = str(rgb[1])
            self.b.text = str(rgb[2])
        else:
            self.r.text = "R"
            self.g.text = "G"
            self.b.text = "B"

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
        return self.pressurize_pressed and self.depressurize_pressed


class RobotImagePane(BoxLayout):
    def __init__(self, robot_image, button_up_cc, button_down_cc, p_img, p_off_img, dp_img, dp_off_img, size_hint=(1, 1), pos_hint={"x": 0, "y": 0}):
        super(RobotImagePane, self).__init__()
        self.size_hint = size_hint
        self.pos_hint = pos_hint
        self.orientation = "horizontal"
        self.padding = 10

        self.button_layout = BoxLayout(orientation="vertical", size_hint=(0.25, 0.7), pos_hint={"x": 0, "center_y": 0.5}, spacing=10)
        self.robot_layout = FloatLayout()

        self.robot_image = ImagePane(robot_image)

        self.pump = RoundToggleButton("Pump (on)", "Pump (off)", button_down_cc, button_up_cc)
        self.gate = RoundToggleButton("Gate (open)", "Gate (closed)", button_down_cc, button_up_cc)
        self.sensors = RoundToggleButton("Sensors (on)", "Sensors (off)", button_down_cc, button_up_cc)

        self.actuator0 = RobotImageBoxButtons(p_img, p_off_img, dp_img, dp_off_img)
        self.actuator1 = RobotImageBoxButtons(p_img, p_off_img, dp_img, dp_off_img)
        self.actuator2 = RobotImageBoxButtons(p_img, p_off_img, dp_img, dp_off_img)
        self.actuator3 = RobotImageBoxButtons(p_img, p_off_img, dp_img, dp_off_img)
        self.actuator4 = RobotImageBoxButtons(p_img, p_off_img, dp_img, dp_off_img)
        self.actuator5 = RobotImageBoxButtons(p_img, p_off_img, dp_img, dp_off_img)

        self.add_widget(self.button_layout)
        self.add_widget(self.robot_layout)

        self.button_layout.add_widget(self.pump)
        self.button_layout.add_widget(self.gate)
        self.button_layout.add_widget(self.sensors)

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
