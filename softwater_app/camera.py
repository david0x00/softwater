import time
import threading
from turtle import width
import cv2
import numpy as np
from rate import Rate


class ImageBuffer:
    def __init__(self, dim1, dim2, dim3=0, buffer_size=4):
        self._buffer_size = buffer_size

        if dim3 != 0:
            self._buffer = np.zeros((buffer_size, dim1, dim2, dim3), dtype=np.float32)
        else:
            self._buffer = np.zeros((buffer_size, dim1, dim2), dtype=np.float32)
        self._new_images = np.zeros((1, buffer_size), dtype=bool)
        self._ptr = 0

    def new_buffer(self):
        a = np.zeros((1, self._buffer_size), dtype=bool)
        self._new_images = np.append(self._new_images, a, axis=0)
        return self._new_images.shape[0] - 1

    def insert(self, image):
        if image is None:
            return
        self._buffer[self._ptr] = image
        for stream in range(self._new_images.shape[0]):
            self._new_images[stream, self._ptr] = True
        self._ptr += 1
        if self._ptr >= self._buffer_size:
            self._ptr = 0
        self._first = True

    def get_latest(self, stream=0):
        pos = self._get_pos()
        is_new = self._new_images[stream, pos]
        if is_new:
            self._new_images[stream, pos] = False
        return is_new, self._buffer[pos]

    def _get_pos(self):
        ptr = self._ptr - 1
        if ptr < 0:
            ptr += self._buffer_size
        return ptr


class Camera:
    def __init__(self, width, height, cam_id=0, fps=30, buffer_size=8, timeout=2):
        self._width = width
        self._height = height
        self._cam_id = cam_id
        self._fps = fps
        self._buffer_size = buffer_size
        self._timeout = timeout

        self._running = False

        self._update_thread = None
        self._imgbuf = ImageBuffer(height, width, 3, buffer_size)
        self._lock = threading.Lock()

        self._cap = cv2.VideoCapture(cam_id)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        self._lastcap = time.time()

    def start(self):
        if not self._running:
            self._running = True
            self._update_thread = threading.Thread(target=self._update)
            self._update_thread.start()

    def pause(self):
        if self._running:
            self._running = False
            self._update_thread.join()

    def close(self):
        self.pause()
        self._cap.release()
        
    def change_settings(self, setting, value):
        if setting == cv2.CAP_PROP_FRAME_WIDTH:
            with self._lock:
                self._imgbuf = ImageBuffer(self._height, value, 3, self._buffer_size)
        if setting == cv2.CAP_PROP_FRAME_HEIGHT:
            with self._lock:
                self._imgbuf = ImageBuffer(value, self._width, 3, self._buffer_size)
            
        self._cap.set(setting, value)

    def is_running(self):
        return self._running

    def get(self, stream):
        self._lastcap = time.perf_counter()
        with self._lock:
            is_new, image = self._imgbuf.get_latest(stream)
        return is_new, image

    def new_stream(self):
        with self._lock:
            res = self._imgbuf.new_buffer()
        return res

    def _update(self):
        rate = Rate(self._fps)
        while self._running:
            if rate.get_start() - self._lastcap >= self._timeout:
                break
            ret, img = self._cap.read()
            if ret:
                img = cv2.resize(img, (self._width, self._height), cv2.INTER_AREA)
                with self._lock:
                    self._imgbuf.insert(img)
            rate.sleep()
        self._cap.release()
