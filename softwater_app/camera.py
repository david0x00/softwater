import cv2
import threading
import queue

class Camera:
    def __init__(self, width=1280, height=720, framerate=30):
        self._camera = cv2.VideoCapture(0)
        self._camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self._camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self._camera.set(cv2.CAP_PROP_FPS, framerate)
        self._framerate = framerate
        self._running = False
        self._thread = threading.Thread(target=self._capture)
        self._queue = queue.Queue(10)
    
    def start(self):
        self._running = True
        self._thread.start()
    
    def stop(self):
        self._running = False
        self._thread.join()
    
    def set(self, setting, value):
        self._camera.set(setting, value)

    def get(self, latest=True):
        img = None
        try:
            if latest:
                while True:
                    img = self._queue.get(block=False)
            else:
                img = self._queue.get()       
        except queue.Empty:
            pass
        return img

    def _capture(self):
        while (self._running):
            ret, image = self._camera.read()
            if (ret):
                self._queue.put(image)