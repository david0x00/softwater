from controller import Controller
from multiprocessing import current_process

if current_process().name != 'MainProcess':
    import keras
import numpy as np
import time

'''
Figure out emergency stop
figure out saving directories
figure out timeout 50 seconds
'''

class IK:
    model_folder = "./ik_model/comb_bmodel/comb_bmodel.h5"

    xmin = -15
    xmax = 15
    ymin = 0
    ymax = 40

    pmin = 95
    pmax = 121

    def __init__(self):
        self.ik_model = keras.models.load_model(self.model_folder)

    def rescale(self, p_list):
        ret = []
        for p in p_list:
            ret.append((p * (self.pmax - self.pmin)) + self.pmin)
        return ret

    def normalize(self, x, y):
        ret = np.zeros(2)
        ret[0] = (x - self.xmin) / (self.xmax - self.xmin)
        ret[1] = (y - self.ymin) / (self.ymax - self.ymin)
        ret = ret.reshape(1,-1)
        return ret
        
    def calc(self, x_ee):
        x = x_ee[0]
        y = x_ee[1]
        x_in = self.normalize(x, y)
        p_norm = self.ik_model.predict(x_in)
        p = self.rescale(list(p_norm[0]))
        return p

class VisualServo(Controller):
    def __init__(self):
        super().__init__()
        

        self.pressure_error_threshold = 0.1

        self.update_target_timeout = 5 

        self.Kp = np.array([
            [0.25],
            [0.5]
        ])
        self.Ki = np.array([
            [0.1],
            [0.1]
        ])
    
    def extra_headers(self):
        headers = [
            "TARGX",
            "TARGY",
            "XEEX",
            "XEEY",
            "ERRORX",
            "ERRORY",
            "DT",
            "INT_ERRX",
            "INT_ERRY",
            "PX",
            "PY",
            "IX",
            "IY",
            "ADJ_TARGX",
            "ADJ_TARGY",
            "TP1L",
            "TP1R",
            "TP2L",
            "TP2R",
        ]
        return headers

    def extra_data(self):
        data = [
            self.target[0],
            self.target[1],
            self.x_ee[0],
            self.x_ee[1],
            self.error[0][0],
            self.error[1][0],
            self.dt,
            self.integration_error[0][0],
            self.integration_error[1][0],
            self.P[0][0],
            self.P[1][0],
            self.I[0][0],
            self.I[1][0],
            self.adjusted_target[0],
            self.adjusted_target[1],
            self.target_pressures[0],
            self.target_pressures[1],
            self.target_pressures[2],
            self.target_pressures[3]
        ]
        return data

    
    def on_start(self):
        print("Controller Start")
        self.adjusted_target = self.target
        self.ik = IK()
        self.target_pressures = self.ik.calc(self.adjusted_target)

        self.update_target_counter = 0
        self.integration_error = np.zeros((2, 1))

        self.start_time = time.perf_counter()
        self.prev_time = self.start_time

        self.dt = 0
        self.error = np.zeros((2, 1))
        self.P = np.zeros((2, 1))
        self.I = np.zeros((2, 1))

    def on_end(self):
        print("Controller End")
    
    def adjust_target(self, x_ee_in):
        # Get dt and reset prev_time
        curr_time = time.perf_counter()
        dt = curr_time - self.prev_time
        self.prev_time = curr_time

        targ = np.array([
            [float(self.target[0])],
            [float(self.target[1])]
        ])

        x_ee = np.array([
            [float(x_ee_in[0])],
            [float(x_ee_in[1])]
        ])

        error = targ - x_ee
        self.integration_error = self.integration_error + (error * dt)

        P = self.Kp * error
        I = self.Ki * self.integration_error

        new_target = targ + P + I

        self.adjusted_target = [new_target[0][0], new_target[1][0]]
        self.dt = dt
        self.error = error
        self.P = P
        self.I = I

        self.target_pressures = self.ik.calc(self.adjusted_target)

    def evaluate(self, x):
        pressures = x[0:4]
        x_ee = x[-2:]
        self.x_ee = x_ee
        u = [False for _ in range(self.solenoid_count)]

        if self.update_target_counter >= self.update_target_timeout:
            self.adjust_target(x_ee)
            self.update_target_counter = 0
        
        self.update_target_counter += 1

        for i in range(self.pressure_sensor_count):
            target_bottom = self.target_pressures[i] - self.pressure_error_threshold
            target_top = self.target_pressures[i] + self.pressure_error_threshold
            if pressures[i] < target_bottom:
                u[i * 2] = True
            elif pressures[i] > target_top:
                u[(i * 2) + 1] = True

        return u

controller = VisualServo()