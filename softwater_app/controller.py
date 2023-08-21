from concurrent.futures import process
from multiprocessing import Process, Queue
import queue
from rate import Rate
import time
import os
import cv2
import csv
import numpy as np

class Controller:
    _cmd_queue = Queue()
    _in_queue = Queue()
    _out_queue = Queue()

    rate = Rate(2)
    timeout = 10
    pressure_sensor_count = 6
    solenoid_count = 12
    target = None

    pressed_valve_state = [False]*12

    t_headers = [
        "TIME"
    ]

    u_headers = [
        "M1-AL-IN", "M1-AL-OUT", "M1-AR-IN", "M1-AR-OUT", 
        "M2-AL-IN", "M2-AL-OUT", "M2-AR-IN", "M2-AR-OUT", 
        "M3-AL-IN", "M3-AL-OUT", "M3-AR-IN", "M3-AR-OUT"
    ]

    x_headers = [
        "M1X", "M1Y", "M2X", "M2Y", "M3X", "M3Y", "M4X", "M4Y", 
        "M5X", "M5Y", "M6X", "M6Y", "M7X", "M7Y", "M8X", "M8Y", 
        "M9X", "M9Y", "M10X", "M10Y", "M11X", "M11Y", "M12X", "M12Y",
        "M13X", "M13Y", "M14X", "M14Y", "M15X", "M15Y", "M16X", "M16Y"
    ]

    p_headers = ["M1-PL", "M1-PR", "M2-PL", "M2-PR", "M3-PL", "M3-PR"]

    a_headers = ["A1", "A2", "A3", "A4"]

    o_headers = [
        "ORIGX", "ORIGY"
    ]

    xc = [[-9,-7,-5,-3,-1,1,3,5,7,9],
          [-9,-7,-5,-3,-1,1,3,5,7,9],
          [-7,-5,-3,-1,1,3,5,7],
          [-5,-3,-1,1,3,5],
          [-3,-1,1,3],
          [-1,1]]
    yc = 25

    ext_goals = [[-13,25],[-13,27],[-13,29],[-11,31],[-9,33],[-7,35],[-5,37],[-3,39],[-1,39],[1,39],[3,39],[5,37],[7,35],[9,33],[11,31],[13,29],[13,27],[13,25]]
    
    def __init__(self):
        self.column_headers = self.package_headers()
        self.img_arr = []
        self.data_dir = "./"

        self.idx_coords = []
        for i, row in enumerate(self.xc):
            for x in row:
                y = self.yc + i*2
                self.idx_coords.append([x,y])
        self.idx_coords += self.ext_goals

    def convert_idx(self, idx):
        ret = self.idx_coords[idx]
        print("Coordinates: " + str(ret))
        return ret
    
    def set_target(self, target):
        self.target = target

    def prepare(self, target):
        self.set_target(target)
        self.img_arr = []
        self.data_file = str(
            self.data_dir
            + "control_data_" 
            + str(int(target[0]))
            + "_"
            + str(int(target[1]))
            + ".csv"
        )
        self.img_count = 0
        self.img_dir = self.data_dir + "imgs/"
        if not os.path.exists(self.img_dir):
            os.makedirs(self.img_dir)
        
        with open(self.data_file, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.column_headers)
            writer.writeheader()

    def stop(self):
        self._cmd_queue.put(None)
    
    def on_start(self):
        pass

    def on_end(self):
        pass
    
    def get_observations(self):
        self._out_queue.put(('app', 'get data'))
        print("waiting")
        t = time.perf_counter()
        while True:
            try:
                data = self._in_queue.get(timeout=1)
                break
            except queue.Empty:
                if self._check_cmd_queue():
                    return None
        
        print(f"got -- {(time.perf_counter() - t) * 1000} ms")
        return data
    
    def evaluate(self, *args):
        u = []
        for _ in range(self.solenoid_count):
            u.append(False)
    
    def implement_controls(self, u):
        self._out_queue.put(('robot', {'command': {'set solenoids': u}}))

    def package_headers(self):
        headers = []
        headers += self.t_headers
        headers += self.x_headers[0:20]
        headers += self.p_headers[:4]
        headers += self.a_headers[:3]
        headers += self.u_headers[:8]
        headers += self.o_headers
        headers += self.extra_headers()
        return headers

    def extra_headers(self):
        return []

    def package_data(self, t, x, p, a, u, o):
        data = [t]
        data += x[2:22]
        data += p[:4]
        data += a[:3]
        data += u[:8]
        data += o
        data += self.extra_data()
        return data

    def extra_data(self):
        return []

    def save_data(self, t, x, p, angles, u, origin, img):
        self.write_img(img)

        with open(self.data_file, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.column_headers)

            data = self.package_data(t, x, p, angles, u, origin)
            row_dict = {}

            for idx, header in enumerate(self.column_headers):
                row_dict[header] = data[idx]
            
            writer.writerow(row_dict)
    
    def write_img(self, img):
        file_name = self.img_dir + 'img' + str(self.img_count) + ".jpg"
        cv2.imwrite(file_name, img)
        self.img_count += 1

    def _check_cmd_queue(self):
        try:
            print(self._cmd_queue.get_nowait())
            return True
        except queue.Empty:
            return False

    def main_loop(self, in_queue, out_queue, cmd_queue):
        self.rate.set_start()
        start = self.rate.get_start()

        if self.target is None:
            return

        self._in_queue = in_queue
        self._out_queue = out_queue
        self._cmd_queue = cmd_queue
        
        # send start command to robot
        out_queue.put(('robot', {'command': {'running': True}}))

        self.on_start()

        while time.perf_counter() < start + self.timeout:
            if self._check_cmd_queue():
                break
            
            # Main Control tasks
            msg = self.get_observations()
            if msg is None:
                break
            t, origin, x, p, num_segments, img, self.pressed_valve_state = msg
            p = p[:2] + p[4:] + p[2:4]
            # lines = x[num_segments * 2:len(x)]
            lines = x[num_segments * 2:]
            angles = []
            # 3 for 2 stage
            # 4 for 3 stage
            for i in range(0, 4*3, 4):
                px = lines[i + 2] - lines[i]
                py = lines[i + 3] - lines[i + 1]
                angles.append(np.degrees(np.arctan2(py, px)))
            # print(x[0:num_segments*2])
            u = self.evaluate(x[0:num_segments * 2], p, angles)
            # print(u)
            self.implement_controls(u)

            # Save Data
            self.save_data(t, x[0:num_segments * 2], p, angles, u, origin, img)

            # emergency stop if pressure exceeeds 118 kPa
            maxp = max(p)
            if maxp > 125 and maxp < 127:
                break

            # Wait for end of control loop
            self.rate.sleep()
        
        # send stop command to robot
        out_queue.put(('robot', ({'command': {'running': False}})))
        out_queue.put(('robot', ({'command': {'rth': True}})))

        self.on_end()


class ControllerHandler:
    controller = None
    _process = None
    
    def __init__(self):
        pass

    def set_controller(self, controller : Controller):
        self.controller = controller
        
    def start(self):
        self._process = Process(target=self.controller.main_loop, args=(self.controller._in_queue, self.controller._out_queue, self.controller._cmd_queue))
        self._process.start()
    
    def is_alive(self):
        return self._process is not None and self._process.is_alive()
    
    def stop(self):
        self.controller._cmd_queue.put(None)
    
    def pipe_out(self):
        if self.controller is None:
            return
        try:
            return self.controller._out_queue.get_nowait()
        except queue.Empty:
            return None
    
    def pipe_in(self, msg):
        if self.controller is None:
            return
        self.controller._in_queue.put(msg)