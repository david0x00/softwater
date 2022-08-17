from concurrent.futures import process
from multiprocessing import Process, Queue
import queue
from rate import Rate
import time
import os
import cv2

class Controller:
    _cmd_queue = Queue()
    _in_queue = Queue()
    _out_queue = Queue()

    rate = Rate(2)
    timeout = 10
    pressure_sensors = 4
    solenoids = 8
    stopped = True
    target = None

    t_headers = [
        "TIME"
    ]

    u_headers = [
        "M1-AL-IN", "M1-AL-OUT", "M1-AR-IN",
        "M1-AR-OUT", "M2-AL-IN", "M2-AL-OUT",
        "M2-AR-IN", "M2-AR-OUT", "PUMP", "GATE"
    ]

    x_headers = [
        "M1-PL", "M1-PR", "M2-PL", "M2-PR", "M1X",
        "M1Y", "M2X", "M2Y", "M3X", "M3Y", "M4X",
        "M4Y", "M5X", "M5Y", "M6X", "M6Y", "M7X",
        "M7Y", "M8X", "M8Y", "M9X", "M9Y", "M10X",
        "M10Y"
    ]
    
    def __init__(self):
        self.column_headers = self.package_headers()
        self.img_arr = []
        self.data_dir = ""

    def prepare(self, target):
        self.target = target
        self.img_arr = []
        self.data_file = str(
            self.data_dir
            + "control_data_" 
            + str(int(target[0]]))
            + "_"
            + str(int(target[1]))
            + ".csv"
        )

    def stop(self):
        if not self.stopped:
            self.stopped = True
            self._cmd_queue.put(None)
    
    def on_start(self):
        pass

    def on_end(self):
        self.write_imgs()
    
    def get_observations(self):
        self._out_queue.put({'command': {'get keyframe': None}})
        print('waiting')
        return self._in_queue.get()
    
    def evaluate(self, x):
        u = []
        for _ in range(self.solenoids):
            u.append(False)
    
    def implement_controls(self, u):
        self._out_queue.put({'command': {'set solenoids': u}})

    def package_headers(self):
        headers = []
        headers += self.t_headers
        headers += self.x_headers
        headers += self.u_headers
        headers += self.extra_headers()
        return headers

    def extra_headers(self):
        return []

    def package_data(self, t, x, u):
        data = []
        data += t
        data += x
        data += u
        data += self.extra_data()
        return data

    def extra_data(self):
        return []

    def save_data(self, t, x, u, img):
        self.img_arr.append(img)

        with open(self.data_file, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.column_headers)

            data = self.package_data(t, x, u)
            row_dict = {}

            for idx, header in enumerate(self.column_headers):
                row_dict[header] = data[idx]
            
            writer.writerow(row_dict)
    
    def write_imgs(self):
        print("Writing Images...")
        img_dir = self.data_dir + "imgs/"
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
        for idx, img in enumerate(self.img_arr):
            file_name = img_dir + str(idx) + ".jpg"
            cv2.imwrite(file_name, img)
        print("Done.")

    def main_loop(self, in_queue, out_queue, cmd_queue):
        start = time.perf_counter()

        if self.target is None:
            return

        self._in_queue = in_queue
        self._out_queue = out_queue
        self._cmd_queue = cmd_queue
        
        # send start command to robot
        out_queue.put({'command': {'running': True}})

        self.on_start()

        while time.perf_counter() < start + self.timeout:
            try:
                cmd_queue.get_nowait()
                break
            except queue.Empty:
                pass
            
            # Main Control tasks
            t, x, img = self.get_observations()
            u = self.evaluate(x)
            self.implement_controls(u)

            # Save Data
            self.save_data(t, x, u, img)

            # Wait for end of control loop
            self.rate.sleep()
        
        # send stop command to robot
        out_queue.put({'command': {'running': False}})

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