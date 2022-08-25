import keras
import threading
import numpy as np
from rate import Rate

class IK:
    model_file = "/Volumes/Flash/comb_bmodel/"

    xmin = -15
    xmax = 15
    ymin = 0
    ymax = 40

    pmin = 95
    pmax = 121

    def __init__(self):
        self.ik_model = keras.models.load_model(self.model_file)

    def rescale(self, p_list):
        ret = []
        for p in p_list:
            ret.append((p * (pmax - pmin)) + pmin)
        return ret

    def normalize(self, x, y):
        ret = np.zeros(2)
        ret[0] = (x - self.xmin) / (self.xmax - self.xmin)
        ret[1] = (y - self.ymin) / (self.ymax - self.ymin)
        ret = ret.reshape(1,-1)
        return ret
        
    def calc(self, p):
        x = p[0]
        y = p[1]
        x_in = self.normalize(x, y)
        q_norm = self.ik_model.predict(x_in)
        q = self.rescale(list(q_norm[0]))
        return q

class RobotState:
    def __init__(self):
        pass



class Controller(threading.Thread):
    freq : int

    _x : np.array
    _u : np.array
    _y : np.array

    save_dir : str

    robot_state : RobotState

    def __init__(self):
        super(Controller, self).__init__()
        self._stop = False
    
    @property
    def x(self):
        return self._x
    
    @property
    def y(self):
        return self._y

    @property
    def u(self):
        return self._u

    @u.setter
    def u(self):
        self.set_u()

    def get_x(self):
        pass

    def get_y(self):
        pass

    def set_u(self):
        pass



    def observe(self):
        pass

    def drive(self, u):
        pass
    
    def run(self):
        rate = Rate(self.freq)
        while not self._stop:
            u = self.step(x)

            x = self.observe()
            u = self.step(x)
            self.drive(u)
            # TODO: Save data
            rate.sleep()
            
    def stop(self):
        self._stop = True
        self.join()
    
    def set_target(self, y):
        self.y = y

    def step(self, x):
        pass


class ClosedLoopIK(Controller):

    def __init__(self, name, freq, save_dir=""):
        super().__init__(save_dir)
        self.inv_kin = IK()
        llc = LowLevelPressure()
        llc.getrobot_state = self.get_x
        llc.set


    def get_x(self):
        pass


    def step(self, x):



class LowLevelPressure(Controller):

