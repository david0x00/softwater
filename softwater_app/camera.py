import cv2
import threading
import queue
import os

os.environ['OPENCV_VIDEOIO_PRIORITY_MSMF'] = '0'

class Camera:
    def __init__(self, width=1920, height=1080, framerate=30):
        self._source = None
        self._width = width
        self._height = height
        self._framerate = framerate
        self._running = False
        self._thread = None
        self._queue = queue.Queue(1)
        self._settings = queue.Queue()
    
    def start(self, source):
        if not self._running: 
            self._source = source
            self._thread = threading.Thread(target=self._capture, daemon=True)
            self._thread.start()
    
    def dims(self):
        return (self._width, self._height)
    
    def change_source(self, source):
        if self._running:
            self.stop()
            self.start(source)
        else:
            self._source = source            
    
    def stop(self):
        if self._running:
            self._running = False
            self._thread.join(timeout=0.2)
    
    def set(self, setting, value):
        self._settings.put((setting, value))
    
    def running(self):
        return self._running

    def get(self, latest=True):
        img = None
        try:
            if latest:
                while True:
                    img = self._queue.get_nowait()
            else:
                img = self._queue.get()       
        except queue.Empty:
            pass
        return img

    def _capture(self):
        if self._source == 0:
            cap = cv2.CAP_ANY
        else:
            cap = cv2.CAP_DSHOW
        camera = cv2.VideoCapture(self._source, cap)
        camera.set(cv2.CAP_PROP_BUFFERSIZE, 0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
        camera.set(cv2.CAP_PROP_FPS, self._framerate)
        self._running = True
        while self._running:
            while not self._settings.empty():
                setting, value = self._settings.get()
                camera.set(setting, value)
            ret, image = camera.read()
            if ret:
                self._queue.put(image)
        camera.release()
