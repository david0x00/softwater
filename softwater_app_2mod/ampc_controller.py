from tracemalloc import start
from controller import Controller
import pickle
import autompc as ampc
import pandas as pd
import numpy as np
from autompc.costs import ThresholdCost
import time
import math
import CQLPolicy
from CQLPolicy import D3RLPyMultiTaskPolicy

class AMPCController(Controller):
    # box cost
    controller_file = "./controller.pkl"
    
    # CQL
    # controller_file = "active_controllers/cql.pkl"

    # Distance cost
    # controller_file = "active_controllers/distance_cost.pkl"

    def __init__(self):
        super().__init__()
        with open(self.controller_file, "rb") as f:
            self.mpc = pickle.load(f)
        self.system = self.mpc.system
        self.ocp = ampc.OCP(self.system)
        # NOTE: Comment out for CQL
        self.mpc.model._device = "cpu"
        
    def extra_headers(self):
        headers = [
            "TARGX",
            "TARGY",
            "XEEX",
            "XEEY",
            "ERRORX",
            "ERRORY",
            "RMSE",
            "AMPCTIME"
        ]
        return headers

    def extra_data(self):
        data = [
            self.target[0],
            self.target[1],
            self.x_ee[0],
            self.x_ee[1],
            self.error[0],
            self.error[1],
            self.rmse,
            self.ampc_dt
        ]
        return data

    def on_start(self):
        print("Controller Start")

        targ = [float(self.target[0]), float(self.target[1])]
        self.ocp.set_cost(
            ThresholdCost(
                system=self.system, goal=targ,
                threshold=1.0, observations=["M10X", "M10Y"]
            )
        )

        for obs in ['M1-PL', 'M1-PR', 'M2-PL', 'M2-PR']:
            self.ocp.set_obs_bound(obs, 97, 118)
        for ctrl in self.system.controls:
            self.ocp.set_ctrl_bound(ctrl, 0, 1)

        self.mpc.set_ocp(self.ocp)
        self.mpc.reset()

        # NOTE: Comment out for CQL
        self.mpc.optimizer.optimizer.log_df = pd.DataFrame(columns=['States', 'Ctrls', 'Cost', 'Quad', 'Barrier', 'ActiveBarrier','BarrierHorizon', 'Timeout'])
        print(self.mpc.optimizer.optimizer.ocp.get_cost()._costs[1].scales)

    def on_end(self):
        # NOTE: Comment out for CQL
        self.mpc.optimizer.optimizer.log_df.to_csv(self.data_dir + '/debug_log.csv')

        print("Model: " + self.controller_file)
        print("Target: " + str(self.target))
        print("End EE Coords: " + str(self.x_ee))
        print("End Distance: " + str(self.rmse))
        print("Controller End")

    def evaluate(self, x):
        start_time = time.perf_counter()
        u = self.mpc.step(x)
        end_time = time.perf_counter()

        self.ampc_dt = (end_time - start_time) * 1000
        self.x_ee = x[-2:]
        self.error = [(self.target[0] - self.x_ee[0]), (self.target[1] - self.x_ee[1])]
        self.rmse = math.sqrt((self.error[0] * self.error[0]) + (self.error[1] * self.error[1]))
        return list(u)

controller = AMPCController()


