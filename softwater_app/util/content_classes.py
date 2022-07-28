from turtle import pos
from util.helpful_kivy_classes import *


class CameraImageSelector(CV2Image, FloatLayout):
    def __init__(self, cc, size_hint=(1, 1), pos_hint={}):
        super(CameraImageSelector, self).__init__()
        self.size_hint = size_hint
        self.pos_hint = pos_hint

        self.rect = Divider(size_hint=(None, None), color_component=cc)
        self.rect.opacity = 0

        self.selecting = False

        self.add_widget(self.rect)

    def on_touch_up(self, touch):
        if (self.selecting):
            self.rect.opacity = 0
            self.selecting = False
            bw, bh = self._forcebounds(touch.pos)
            
            w = float(self.img_size[0])
            h = float(self.img_size[1])

            if (bw == 0 or bh == 0):
                return

            pos = (self.pos[0] + (self.size[0] - self.img_size[0]) / 2, h + self.pos[1] + (self.size[1] - self.img_size[1]) / 2)

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

            zoom[0][0] = zx1 + zoom[0][0] * (zx2 - zx1)
            zoom[0][1] = zy1 + zoom[0][1] * (zy2 - zy1)
            zoom[1][0] = zx1 + zoom[1][0] * (zx2 - zx1)
            zoom[1][1] = zy1 + zoom[1][1] * (zy2 - zy1)

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

        self.button_layout = BoxLayout(orientation="vertical", size_hint=(0.35, 0.7), pos_hint={"x": 0, "center_y": 0.5}, spacing=10)
        self.image = CameraImageSelector(select_cc, size_hint=(1, 0.9), pos_hint={"center_x": 0.5, "center_y": 0.5})

        self.camera_view = RoundToggleButton("Camera", "Camera", button_down_cc, button_up_cc)
        self.tracker_view = RoundToggleButton("Tracker", "Tracker", button_down_cc, button_up_cc)
        self.reset = RoundToggleButton("Reset", "Reset", button_down_cc, button_up_cc)

        self.add_widget(self.button_layout)
        self.add_widget(self.image)

        self.button_layout.add_widget(self.camera_view)
        self.button_layout.add_widget(self.tracker_view)
        self.button_layout.add_widget(self.reset)

        self.camera_view.add_callback(self._camera_view_pressed)
        self.tracker_view.add_callback(self._tracker_view_pressed)
        self.reset.add_callback(self._reset_button_pressed)

        self.camera_view_pressed = True
        self.tracker_view_pressed = False

        self.camera_view.state = "down"
    
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
