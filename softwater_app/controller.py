from concurrent.futures import process
from multiprocessing import Process, Queue
import queue
from rate import Rate
import time


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
    
    def __init__(self):
        pass

    def prepare(self, target):
        self.target = target

    def stop(self):
        if not self.stopped:
            self.stopped = True
            self._cmd_queue.put(None)
    
    def on_start(self):
        pass

    def on_end(self):
        pass
    
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
            x = self.get_observations()
            u = self.evaluate(x)
            self.implement_controls(u)
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