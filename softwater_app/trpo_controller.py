import torch
import torch.nn as nn
from torch.distributions import Categorical
import numpy as np

from controller import Controller

PRESSURE_MIN_VAL = 96
PRESSURE_MAX_VAL = 123.1

X_MARKER_MIN_VAL = -18 
X_MARKER_MAX_VAL = 18

Y_MARKER_MIN_VAL = 0
Y_MARKER_MAX_VAL = 39

SOLENOID_MIN_VAL = 0
SOLENOID_MAX_VAL = 1

## Normalize within the range [-1,+1]
def scale_data(data, pressure=False, x_marker=False, y_marker=False, solenoid=False):
    if pressure:
        min_val = PRESSURE_MIN_VAL
        max_val = PRESSURE_MAX_VAL
    elif x_marker:
        min_val = X_MARKER_MIN_VAL
        max_val = X_MARKER_MAX_VAL
    elif y_marker:
        min_val = Y_MARKER_MIN_VAL
        max_val = Y_MARKER_MAX_VAL
    elif solenoid:
        min_val = SOLENOID_MIN_VAL
        max_val = SOLENOID_MAX_VAL

    return (2*((data - min_val) / (max_val - min_val))) - 1

class TRPOController(Controller):
    controller_file = "../baseline/actor_trpo.pt"

    def __init__(self):
        super().__init__()
        self.agent = torch.load(self.controller_file)
        self.agent.eval()
        self.target = (7,27)
    
    def on_start(self):
        print("TRPO Start")
    
    def on_end(self):
        print("TRPO end")
    
    def evaluate(self, x):
        x_m = np.array(x[4::2])
        y_m = np.array(x[5::2])
        x_m_s = scale_data(x_m, x_marker=True)
        y_m_s = scale_data(y_m, y_marker=True)
        x_t = scale_data(self.target[0], x_marker=True)
        y_t = scale_data(self.target[1], y_marker=True)
        x_ee = x_m_s[-1]
        y_ee = y_m_s[-1]
        e_x = x_t - x_ee
        e_y = y_t - y_ee
        stuff = np.array([
            x_t, y_t, e_x, e_y
        ])
        curr_state = np.concatenate((stuff, x_m_s, y_m_s), 0)
        curr_state = torch.tensor(curr_state).float().unsqueeze(0)
        dist = Categorical(self.agent(curr_state))
        number = dist.sample().item()
        u = [False for _ in range(self.solenoid_count)]
        u[number] = True
        print(u)
        return u


controller = TRPOController()