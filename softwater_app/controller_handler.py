import threading
import queue
from rate import Rate


class ControllerHandler(threading.Thread):
    def __init__(self):
        super(ControllerHandler, self).__init__()

        self._running = True
        self._in_queue = queue.Queue()
        self._out_queue = queue.Queue()
        self._cv = threading.Condition()
        self._controller = None
    
    def set_controller(self, controller):
        if not self._running:
            self._controller = controller
    
    def pipe_out(self):
        try:
            return self._out_queue.get_nowait()
        except queue.Empty:
            return None
    
    def pipe_in(self, msg):
        self._in_queue.put(msg)
        with self._cv:
            self._cv.notify_all()

    def stop(self):
        self._running = False
        self.join()
    
    def _msg_in_queue(self):
        return not self._in_queue.empty() or self._running
    
    def _clear_q(self, q):
        while True:
            try:
                q.get_nowait()
            except queue.Empty:
                return

    def run(self):
        self._clear_q(self._in_queue)
        self._clear_q(self._out_queue)
        if self._controller is None:
            return
        
        rate = Rate(10)
        self._running = True

        self._out_queue.put({'command': {'pump': True}})
        self._out_queue.put({'command': {'gate': True}})

        while self._running:
            self._out_queue.put({'command': {'get keyframe': None}})
            
            while self._running:
                with self._cv:
                    self._cv.wait_for(self._msg_in_queue())
                if not self._running:
                    return
            
            keypoints, pvalues = self._in_queue.get()

            # call function


            values = [False, False, False, False, False, False, False, False]
            self._out_queue.put({'command': {'set solenoids': values}})
            rate.sleep()
        
        self._out_queue.put({'command': {'pump': False}})
        self._out_queue.put({'command': {'gate': False}})
