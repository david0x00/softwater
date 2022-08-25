import time


class Rate:
    def __init__(self, rate):
        self._rate = rate
        self._inv_rate = 1 / rate
        self._cycles = 0
        self._missed = 0
        self._start = time.perf_counter()

    def set_start(self):
        self._start = time.perf_counter()

    def get_start(self):
        return self._start

    def get_rate(self):
        return self._rate

    def get_inverse_rate(self):
        return self._inv_rate

    def sleep(self, set_start=True):
        diff = self._inv_rate + self._start - time.perf_counter()
        if diff >= 0:
            time.sleep(diff)
        else:
            self._missed += 1
        self._cycles += 1
        if set_start:
            self._start = time.perf_counter()

    def fps(self):
        fps = 1 / (time.perf_counter() - self._start)
        return fps

    def ready(self, set_start=True):
        if self._inv_rate <= time.perf_counter() - self._start:
            if set_start:
                self._start = time.perf_counter()
            return True
        return False

    def cycles(self):
        return self._cycles, self._missed