from controller import Controller
import numpy as np
import time

class RandomController(Controller):
    def __init__(self):
        super().__init__()
    
    def on_start(self):
        print("Controller Start")
    
    def on_end(self):
        print("Controller End")

    def evaluate(self, *args):
        pressures = args[1]
        # pressures = x[0:6]
        u = [False for _ in range(len(self.u_headers))]
        
        left = np.random.randint(3)
        right = np.random.randint(3)
        
        left_in = 0
        left_out = 1
        left_pressure = 0
        if left == 0:
            u[left_out] = True
        elif left == 2:
            if pressures[left_pressure] < 118.5:
                u[left_in] = True

        right_in = 2
        right_out = 3
        right_pressure = 1
        if right == 0:
            u[right_out] = True
        elif left == 2:
            if pressures[right_pressure] < 118.5:
                u[right_in] = True

        return u

controller = RandomController()
