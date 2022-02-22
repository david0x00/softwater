import csv
import os
import threading
import time
import random
import math
import datetime
import queue
import numpy as np
from functools import partial

import io

import autompc as ampc
import pickle

try:
    from picamera import PiCamera
    from picamera.array import PiRGBArray
    import cv2
    print("Camera detected!")
    camera_detected = True
except ModuleNotFoundError:
    print("No camera module detected")
    camera_detected = False

try:
    import board
    import busio

    i2c = busio.I2C(board.SCL, board.SDA)
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn

    ads_0 = ADS.ADS1115(i2c, address=0x48)
    ads_1 = ADS.ADS1115(i2c, address=0x49)

    from adafruit_mcp230xx.mcp23008 import MCP23008

    mcp_0 = MCP23008(i2c, address=0x20)
    mcp_1 = MCP23008(i2c, address=0x21)

    from hat.Raspi_MotorHAT import Raspi_MotorHAT, Raspi_DCMotor

    mh = Raspi_MotorHAT(addr=0x6f)
    pump = mh.getMotor(1)
    gate_valve = mh.getMotor(2)

    robot_detected = True
    print("Robot Connected!")

except NotImplementedError:
    print("Robot not Connected: Not Implemented Error")
    ads_0 = -1
    ads_1 = -1
    mcp_0 = -1
    mcp_1 = -1
    robot_detected = False

except ValueError:
    print("Robot not Connected: Value Error")
    ads_0 = -1
    ads_1 = -1
    mcp_0 = -1
    mcp_1 = -1
    robot_detected = False

mtx = np.array([
    [1535.10668, 0, 954.393136],
    [0, 1530.80529, 543.030187],
    [0,0,1]
])

newcameramtx = np.array([
    [1559.8905, 0, 942.619458],
    [0, 1544.98389, 543.694259],
    [0,0,1]
])

inv_camera_mtx = np.linalg.inv(newcameramtx)

dist = np.array([[0.19210016, -0.4423498, 0.00093771, -0.00542759, 0.25832642 ]])

camera_to_markers_dist = 57.055 #cm

def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))

class Camera:

    def __init__(self,directory=""):
        self.camera = PiCamera(sensor_mode=5, framerate=30)
        #self.camera = cv2.VideoCapture(0)
        self.directory = directory
        #self.cap = cv2.VideoCapture(0)
        #self.stream = io.BytesIO()
        self.cv_image = PiRGBArray(self.camera)

    def read(self):
        return self.cap.read()

    def capture(self, count):
        file_name = self.directory + "/" + str(count) + ".jpg"
        self.camera.capture(file_name, use_video_port=True)
        #ret, frame = self.camera.read()
        #cv2.imwrite(file_name, frame)
        print("Captured")

    def get_opencv_img(self):
        self.cv_image.truncate(0)
        self.camera.capture(self.cv_image, "bgr", use_video_port=True)
        #data = np.fromstring(self.stream.getvalue(), dtype=np.uint8)
        #image = cv2.imdecode(data, 1)
        return self.cv_image.array

    def snap(self, filename):
        self.camera.capture(filename, use_video_port=True)
    
    def preview(self):
        self.camera.start_preview()
        time.sleep(5)
        self.camera.stop_preview()


class MarkerDetector:
    """Handles the conversion of photo to marker values."""

    bounding_box_dim = math.floor(65 / 2)

    def __init__(self, init_img, colorthreshold):
        self.lower = colorthreshold[0]
        self.upper = colorthreshold[1]
        self.init_undistort(init_img)
        self.currentStates = self.analyze_thresh_pix(init_img)
    
    def init_undistort(self, init_img):
        # OLD WAY
        # undistorted_img = cv2.undistort(img, mtx, dist, None, newcameramtx)
        # img = cv2.imread(init_image)
        img = init_img
        h = img.shape[0]
        w = img.shape[1]
        self.mapx, self.mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w,h), cv2.CV_32FC1)

    def get_red_mask(self, image, blur):
        # hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        blur_img = cv2.GaussianBlur(image, blur, 0)
        red_mask = cv2.inRange(blur_img, self.lower, self.upper)
        red_mask = cv2.erode(red_mask, None, iterations=3)
        red_mask = cv2.dilate(red_mask, None, iterations=3)
        return red_mask

    def analyze_thresh(self, img):
        pixel_coords = self.analyze_thresh_pix(img)
        return self.pix2world(pixel_coords)

    # Note: Analyzes images by using basic pixel thresholding method.
    #       Computes marker locations (pixels) and returns.
    def analyze_thresh_pix(self, img):
        # Get image and undistort.
        # img = cv2.imread(img_name)
        undistorted_img = cv2.remap(img, self.mapx, self.mapy, interpolation=cv2.INTER_LINEAR)

        # Mask out all non-red pixels.
        red_mask = self.get_red_mask(undistorted_img, (3, 3))
        cv2.imwrite("test_undistort.jpg", undistorted_img)
        cv2.imwrite("test_masked.jpg", red_mask)

        # Draw circles around clusters of red pixels.
        contours, hierarchy = cv2.findContours(red_mask,
                                               cv2.RETR_EXTERNAL,
                                               cv2.CHAIN_APPROX_SIMPLE)

        # Get relevant circles into a list.
        center_list = []
        for c in contours:
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            if x > 300 and x < 1750:
                center_list.append((x, y))
        
        # Check for error.
        if len(center_list) != 11:
            print("Incorrect Marker Detection...")
            # TODO: Make program run the full sweep if it loses markers
            return None
        
        return center_list

    def analyze_threshold_fast(self, img):
        pixel_coords = self.analyze_threshold_fast_pix(img)
        return self.pix2world(pixel_coords)

    def analyze_threshold_fast_pix(self, img):
        #img = cv2.imread(img_name)
        # undistorted_img = cv2.undistort(img, mtx, dist, None, newcameramtx)
        undistorted_img = cv2.remap(img, self.mapx, self.mapy, interpolation=cv2.INTER_LINEAR)
        imageX, imageY, _ = undistorted_img.shape

        newCenters = []
        for i, marker in enumerate(self.currentStates):
            #print(marker)
            x = math.floor(marker[0])
            y = math.floor(marker[1])
            # crop based on pervious positions [y1:y2, x1:x2] making top left (x1, y1) to bottom right (x2, y2)
            y1 = clamp(0, y - self.bounding_box_dim, imageY)
            y2 = clamp(0, y + self.bounding_box_dim, imageY)
            x1 = clamp(0, x - self.bounding_box_dim, imageX)
            x2 = clamp(0, x + self.bounding_box_dim, imageX)

            markerGuess = undistorted_img[y1:y2, x1:x2]
            # cv2.imwrite("box/box" + str(i) + ".jpg", markerGuess)

            red_mask = self.get_red_mask(markerGuess, (3,3))
            # cv2.imwrite("box/box_mask" + str(i) + ".jpg", red_mask)
            edged = red_mask.copy()
            contours, hierarchy = cv2.findContours(red_mask,
                                            cv2.RETR_EXTERNAL,
                                            cv2.CHAIN_APPROX_SIMPLE)

            if len(contours) > 0:
                circle = cv2.minEnclosingCircle(contours[0])
                self.currentStates[i] = circle[0] + np.array([x - self.bounding_box_dim,y - self.bounding_box_dim])
            #newCenters.append(circle[0] + np.array([x - half_bounding_box_pixel_length,y - half_bounding_box_pixel_length])) # (x,y) position of circle in pixels

        return self.currentStates
        #self.currentStates = newCenters
        #return newCenters


    def pix2world(self, center_list):
        # Convert pixel coordinates to world coordinates.
        center_list.sort(key=lambda x: x[1])
        center_list.reverse()

        center_list_3d = []
        for center in center_list:
            coord_2d = np.array([[center[0]],
                                [center[1]],
                                [1]])
            coord_3d = np.matmul(inv_camera_mtx, coord_2d) * camera_to_markers_dist
            center_list_3d.append((coord_3d[0][0], coord_3d[1][0]))
        
        base_point = center_list_3d[0]
        x_base = base_point[0]
        y_base = base_point[1]

        # Package up data and return.
        row_dict = {}
        for idx in range(11):
            x_key = "M" + str(idx) + "X"
            y_key = "M" + str(idx) + "Y"
            t_key = "M" + str(idx) + "T"

            x_val = center_list_3d[idx][0] - x_base
            y_val = y_base - center_list_3d[idx][1]
            t_val = 0

            row_dict[x_key] = x_val
            row_dict[y_key] = y_val
            row_dict[t_key] = t_val

        return row_dict

class PumpAndGate(threading.Thread):
    to_exit = False
    pump_activated = False
    gate_valve_activated = False

    def __init__(self, threadID, hardware_mapper=None):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.hardware_mapper = hardware_mapper
    
    def set_pump(self, val):
        if val == False:
            if self.pump_activated:
                self.hardware_mapper.turnOffPump()
        else:
            if not self.pump_activated:
                self.hardware_mapper.turnOnPump()
        self.pump_activated = val
    
    def set_gate(self, val):
        if val == False:
            if self.gate_valve_activated:
                self.hardware_mapper.closeGateValve()
        else:
            if not self.gate_valve_activated:
                self.hardware_mapper.openGateValve()
        self.gate_valve_activated = val

    def switchPump(self):
        self.pump_activated = not self.pump_activated
        if self.hardware_mapper is not None:
            if self.pump_activated:
                self.hardware_mapper.turnOnPump()
            else:
                self.hardware_mapper.turnOffPump()
        print("Switch Pump " + str(self.pump_activated))

    def switchGateValve(self):
        self.gate_valve_activated = not self.gate_valve_activated
        if self.hardware_mapper is not None:
            if self.gate_valve_activated:
                self.hardware_mapper.openGateValve()
            else:
                self.hardware_mapper.closeGateValve()
        print("Switch Gate Valve " + str(self.gate_valve_activated))


class PressureSensor(threading.Thread):
    timer = 0
    id = 0
    to_exit = False

    def __init__(self, threadID, number, frequency, hardware_mapper=None):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.id = number
        self.timer = frequency
        self.hardware_mapper = hardware_mapper
        self.num_of_tries = 5

    def run(self):
        pass

    def read_sensor(self):
        if self.hardware_mapper is not None:
            #print("Sensor " + str(self.id) + "reads: " + str(self.hardware_mapper.readSensor(self.id)))
            for i in range(self.num_of_tries):
                try:
                    return self.hardware_mapper.readSensor(self.id)
                except OSError:
                    print("try: " + str(i))
            return -1
        else:
            randomnum = random.uniform(0, 10)
            #print("Sensor " + str(self.id) + "reads: " + str(randomnum))
            return randomnum

    def getID(self):
        return self.threadID

    def terminate(self):
        self.to_exit = True


class HardwareMapping:

    def __init__(self):
        self.actuator_pin_order = [2, 3, 1, 0]
        self.actuator_boards = [mcp_0, mcp_1]
        self.setupPins()

        self.sensor_pairs = [(ads_0, ADS.P1), (ads_0, ADS.P0), (ads_1, ADS.P1), (ads_1, ADS.P0)]

    def setupPins(self):
        self.pins = []
        for module in self.actuator_boards:
            for pin_num in self.actuator_pin_order:
                temp_pin = module.get_pin(pin_num)
                temp_pin.switch_to_output(value=False)
                self.pins.append(temp_pin)

    def actuateSolenoid(self, id, new_state):
        self.pins[id].value = new_state

    def readSensor(self, id):
        sensor_pair = self.sensor_pairs[id]
        chan = AnalogIn(sensor_pair[0], sensor_pair[1])
        Va = chan.voltage
        P = ((Va / 5.0) + 0.040) / 0.004  # kilopascels
        return P

    def turnOnPump(self):
        pump.run(Raspi_MotorHAT.BACKWARD)
        pump.setSpeed(100)

    def turnOffPump(self):
        pump.run(Raspi_MotorHAT.RELEASE)
        pump.setSpeed(0)

    def openGateValve(self):
        gate_valve.run(Raspi_MotorHAT.FORWARD)
        gate_valve.setSpeed(100)

    def closeGateValve(self):
        gate_valve.run(Raspi_MotorHAT.RELEASE)
        gate_valve.setSpeed(0)


class Actuator(threading.Thread):
    id = 0
    is_depressurizer = False
    activated = False

    def __init__(self, threadID, id, is_depressurizer, hardware_mapper=None):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.id = id
        self.is_depressurizer = is_depressurizer
        self.hardware_mapper = hardware_mapper

    def run(self):
        print()
    
    def set_val(self, val):
        if val == False:
            if self.activated:
                self.hardware_mapper.actuateSolenoid(self.id, val)
        else:
            if not self.activated:
                self.hardware_mapper.actuateSolenoid(self.id, val)
        self.activated = val


    def switch(self):
        self.activated = not self.activated
        if self.hardware_mapper is not None:
            self.hardware_mapper.actuateSolenoid(self.id, self.activated)
        print("Actuator " + str(self.id) + " Move " + str(self.activated))

    def getID(self):
        return self.threadID

    def get_is_depressurizer(self):
        return self.is_depressurizer

    def get_state(self):
        return self.activated


class WaterRobot(threading.Thread):
    frequency = 2
    pressure_sensors = []
    actuators = []
    to_exit = False
    sensors_have_started = False
    data_filepath = ''
    detected_status = robot_detected
    values = []
    is_taking_data = False
    actuator_command_queue = queue.Queue()
    gate_mask = np.array([1, 0, 1, 0, 1, 0, 1, 0])
    csv_headers = ["TIME", "M1-PL", "M1-PR", "M2-PL", "M2-PR", "M1-AL-IN", "M1-AL-OUT", "M1-AR-IN", "M1-AR-OUT", "M2-AL-IN", "M2-AL-OUT", "M2-AR-IN", "M2-AR-OUT", "PUMP", "GATE"]
    control_headers = ["TIME", "M1-AL-IN", "M1-AL-OUT", "M1-AR-IN",
                       "M1-AR-OUT", "M2-AL-IN", "M2-AL-OUT", "M2-AR-IN",
                       "M2-AR-OUT", "PUMP", "GATE", "M1-PL", "M1-PR", "M2-PL",
                       "M2-PR", "M1X", "M1Y", "M2X", "M2Y", "M3X", "M3Y",
                       "M4X", "M4Y", "M5X", "M5Y", "M6X", "M6Y", "M7X", "M7Y",
                       "M8X", "M8Y", "M9X", "M9Y", "M10X", "M10Y"]

    def __init__(self, numSensors, numActuators):
        threading.Thread.__init__(self)
        self.threadID = "ROBOTMAIN"
        print("Robot Init.")

        current_directory = os.getcwd()
        final_directory = os.path.join(current_directory, r'data')
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)

        if robot_detected:
            self.hardware_mapper = HardwareMapping()
        else:
            self.hardware_mapper = None
        
        if camera_detected:
            self.camera = Camera()
        else:
            self.camera = None


        for i in range(0, numSensors):
            sensor = PressureSensor(i, i, 1000, hardware_mapper=self.hardware_mapper)
            self.pressure_sensors.append(sensor)
            self.values.append(0)
        for j in range(0, numActuators):
            is_dep = False
            if (j % 2):
                is_dep = True
            self.actuators.append(Actuator(j, j, is_dep, hardware_mapper=self.hardware_mapper))

        self.pump_and_gate = PumpAndGate(0, self.hardware_mapper)

    def getRedMask(self, image, lower, upper):
        hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        blur_img = cv2.GaussianBlur(hsv_img, (25,25), 0)
        red_mask = cv2.inRange(blur_img, lower, upper)
        red_mask = cv2.erode(red_mask, None, iterations=3)
        red_mask = cv2.dilate(red_mask, None, iterations=3)
        return red_mask

    def get_observations(self):
        img = self.camera.get_opencv_img()

        init_markers = self.md.analyze_threshold_fast(img)
        marker_keys = list(init_markers.keys())

        for i in range(4):
            self.obs[i] = round(self.pressure_sensors[i].read_sensor(), 3)

        for i in range(1, 11):
            key1 = marker_keys[i*3]
            key2 = marker_keys[i*3 + 1]
            self.obs[(i - 1)*2 + 4] = init_markers[key1]
            self.obs[(i - 1)*2 + 5] = init_markers[key2]

    def control(self):
        # Algorithm:
        # Initalize control loop
        # color_threshold = (np.array([40, 61, 157]), np.array([255, 255, 255]))
        color_threshold = (np.array([0, 0, 150]), np.array([130, 130, 255]))
        init_img = self.camera.get_opencv_img()
        self.md = MarkerDetector(init_img, color_threshold)

        self.obs = np.zeros(24)

        self.get_observations()

        # Initialize autompc
        with open("controller.pkl", "rb") as f:
            controller = pickle.load(f)
        system = controller.system
        # create tajectory for history
        traj = ampc.zeros(system, 1)
        traj[0].obs[:] = self.obs
        # generate the controller state
        # constate = controller.traj_to_state(traj)
        controller.model._device = "cpu"
        print(system.observations)
        print(system.controls)

        os.remove("data/control_test.csv")
        with open('data/control_test.csv', 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.control_headers)
            writer.writeheader()
        
        self.u = controller.run(self.obs)
        self.implement_controls()

        start_time = datetime.datetime.now()
        loop_number = 0
        loop_period = 0.5
        timer = 100
        while 1:
            curr_time = datetime.datetime.now()
            elapsed_time = (curr_time - start_time).total_seconds()

            if elapsed_time > timer:
                break

            proposed_loop_number = int(elapsed_time / loop_period)
            if proposed_loop_number > loop_number:
                print(elapsed_time)
                loop_number = proposed_loop_number
                self.get_observations()
                self.u = controller.run(self.obs)
                self.implement_controls()
                self.save_control_state(start_time)
            
        self.turn_off_robot()
        print("Done!")
        
    def save_control_state(self, st):
        with open('data/control_test.csv', 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.control_headers)

            current_time = datetime.datetime.now()
            elapsed_time = round((current_time - st).total_seconds(),3)

            row_dict = {}
            for idx, h in enumerate(self.control_headers):
                if idx == 0:
                    row_dict[h] = elapsed_time
                elif idx > 0 and idx < 9:
                    row_dict[h] = self.u[idx - 1]
                elif idx == 9:
                    row_dict[h] = 1
                elif idx == 10:
                    x = (self.u * self.gate_mask).sum()
                    if x:
                        row_dict[h] = 1
                    else:
                        row_dict[h] = 0
                elif idx >= 11 and idx < 35:
                    row_dict[h] = self.obs[idx - 11]

            writer.writerow(row_dict)

    def turn_off_robot(self):
        self.set_pump(False)
        self.set_gate_valve(False)
        for i in range(8):
            self.set_solenoid(i, False)


    def implement_controls(self):
        print(self.u)
        self.set_pump(True)

        x = (self.u * self.gate_mask).sum()
        if x:
            self.set_gate_valve(True)
        else:
            self.set_gate_valve(False)

        for i in range(len(self.u)):
            u_val = bool(self.u[i])
            self.set_solenoid(i, u_val)

    def tune_cv(self):
        pass

    def getListOfParts(self):
        for i in self.pressure_sensors:
            print("Pressure Sensor " + str(i.getID))
        for j in self.actuators:
            print("Actuator " + str(j.getID))

    def pause(self):
        pass

    def stop(self):
        print("Sensor Shutdown")
        self.to_exit = True
    
    def switchPump(self):
        if self.is_taking_data:
            self.actuator_command_queue.put(self.pump_and_gate.switchPump)
        else:
            self.pump_and_gate.switchPump()
    
    def switchGateValve(self):
        if self.is_taking_data:
            self.actuator_command_queue.put(self.pump_and_gate.switchGateValve)
        else:
            self.pump_and_gate.switchGateValve()
        pass

    def __read_sensor(self, id):
        self.values[id] = round(self.pressure_sensors[id].read_sensor(), 3)

    def read_sensor(self, id: int):
        if (id < len(self.pressure_sensors) and id >= 0):
            self.__read_sensor(id)

    def __actuate_solenoid(self, id):
        self.actuators[id].switch()
    
    def set_solenoid(self, id, val):
        self.actuators[id].set_val(val)
    
    def set_gate_valve(self, val):
        self.pump_and_gate.set_gate(val)
    
    def set_pump(self, val):
        self.pump_and_gate.set_pump(val)

    def actuate_solenoid(self, id: int):
        if (id < len(self.actuators) and id >= 0):
            if self.is_taking_data:
                self.actuator_command_queue.put(partial(self.__actuate_solenoid, id))
            else:
                self.__actuate_solenoid(id)
    
    def runActuatorCommands(self):
        while not self.actuator_command_queue.empty():
            func = self.actuator_command_queue.get()
            func()

    def run(self):
        self.is_taking_data = True

        if self.camera is not None:
            self.images_directory = "/".join(self.data_filepath.split("/")[:-1]) + "/" + self.data_filepath.split("/")[-1].split(".")[0] + "/"
            if not os.path.exists(self.images_directory):
                os.makedirs(self.images_directory)
            self.camera.directory = self.images_directory

        with open(self.data_filepath, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.csv_headers)
            writer.writeheader()
        
        self.sample_count = 0
        self.start_time = datetime.datetime.now()

        while (self.to_exit == False):
            time.sleep(1 / self.frequency)
            self.runActuatorCommands()
            self.saveState()
        
        self.is_taking_data = False
        self.actuator_command_queue = queue.Queue()
        print("Experiment Summary")
        print("Total time: " + str(self.elapsed_time))
        print("Total samples: " + str(self.sample_count))
    
    def startTimer(self):
        self.test_begin_time = datetime.datetime.now()

    def endTimer(self, message):
        self.test_end_time = datetime.datetime.now()
        self.test_elapsed_time = (self.test_end_time-self.test_begin_time).total_seconds()
        print(message + ": " + str(self.test_elapsed_time))

    def saveState(self):
        with open(self.data_filepath, 'a', newline='') as file:
            #writer = csv.DictWriter(file, fieldnames=['sensors', 'actuators'])
            writer = csv.DictWriter(file, fieldnames=self.csv_headers)

            self.startTimer()
            if self.camera is not None:
                self.camera.capture(self.sample_count)
            self.endTimer("Camera Capture")
            self.startTimer()
            current_time = datetime.datetime.now()
            self.elapsed_time = round((current_time - self.start_time).total_seconds(),3)

            for i in range(0, len(self.values)):
                self.values[i] = round(self.pressure_sensors[i].read_sensor(), 3)

            actuatorvalues = []
            for i in self.actuators:
                actuatorvalues.append(i.activated * 1)
            
            row_dict = {}
            for idx, h in enumerate(self.csv_headers):
                if idx == 0:
                    row_dict[h] = self.elapsed_time
                elif idx > 0 and idx < 5:
                    row_dict[h] = self.values[idx - 1]
                elif idx >= 5 and idx < 13:
                    row_dict[h] = actuatorvalues[idx - 5]
                elif idx == 13:
                    row_dict[h] = self.pump_and_gate.pump_activated * 1
                elif idx == 14:
                    row_dict[h] = self.pump_and_gate.gate_valve_activated * 1

            #writer.writerow({'sensors': self.values, 'actuators': actuatorvalues})
            writer.writerow(row_dict)
            self.sample_count += 1
            self.endTimer("everything else")

    def printOut(self, text):
        print(text)


def main():
    print()


if __name__ == "__main__":
    main()
