from controller import Controller
import time
import pickle
# import visual_servo
# from multiprocessing import current_process

# # import keras
# if current_process().name != 'MainProcess':
#     import keras
# import numpy as np

# class IK:
#     model_folder = "./ik_model/comb_bmodel/comb_bmodel.h5"

#     xmin = -15
#     xmax = 15
#     ymin = 0
#     ymax = 40

#     pmin = 95
#     pmax = 121

#     def __init__(self):
#         self.ik_model = keras.models.load_model(self.model_folder)

#     def rescale(self, p_list):
#         ret = []
#         for p in p_list:
#             ret.append((p * (self.pmax - self.pmin)) + self.pmin)
#         return ret

#     def normalize(self, x, y):
#         ret = np.zeros(2)
#         ret[0] = (x - self.xmin) / (self.xmax - self.xmin)
#         ret[1] = (y - self.ymin) / (self.ymax - self.ymin)
#         ret = ret.reshape(1,-1)
#         return ret
        
#     def calc(self, x_ee):
#         x = x_ee[0]
#         y = x_ee[1]
#         x_in = self.normalize(x, y)
#         p_norm = self.ik_model.predict(x_in)
#         p = self.rescale(list(p_norm[0]))
#         return p


class SimpleController(Controller):
    def __init__(self, target_data):
        super().__init__()
        # self.ik = visual_servo.IK()
        self.ik = None
        with open(target_data, 'rb') as f:
            self.controller_pressures = pickle.load(f)['comb']
        self.timeout = 20
    
    def on_start(self):
        print("Controller Start")
        self.target_pressures = self.ik.calc(self.target)

    def on_end(self):
        print("Controller End")
        
    def update_target(self, new_target):
        if new_target is None:
            return

        self.target = new_target
    
    def set_ik(self, ik):
        self.ik = ik

    def evaluate(self, x, p, angles):
        pressures = p
        x_ee = x[-2:]
        self.x_ee = x_ee
        u = [False for _ in range(self.solenoid_count)]
    # def evaluate(self, x):
    #     pressures = x[0:4]
    #     u = [False for _ in range(self.solenoid_count)]

        # target_pressures = self.controller_pressures[self.target]
        self.target_pressures = self.ik.calc(self.target)

        for i in range(4):
            if pressures[i] < self.target_pressures[i]:
                u[i * 2] = True
        return u

controller = SimpleController("./simple_controller_old.p")
