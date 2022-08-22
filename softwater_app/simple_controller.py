from controller import Controller
import time
import pickle


class SimpleController(Controller):
    def __init__(self, target_data):
        super().__init__()
        with open(target_data, 'rb') as f:
            self.controller_pressures = pickle.load(f)['comb']
        self.timeout = 20
    
    def on_start(self):
        print("Controller Start")

    def on_end(self):
        print("Controller End")

    def evaluate(self, x):
        pressures = x[0:4]
        u = [False for _ in range(self.solenoid_count)]

        target_pressures = self.controller_pressures[self.target]

        for i in range(self.pressure_sensor_count):
            if pressures[i] < target_pressures[i]:
                u[i * 2] = True
        return u

controller = SimpleController("./simple_controller_old.p")
