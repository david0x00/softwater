from tracemalloc import start
from controller import Controller
import pickle
import autompc as ampc
import pandas as pd
import numpy as np
from autompc.costs import ThresholdCost
import time
import math
# import d3rlpy
# import copy
# import gym
# import CQLPolicy
# from CQLPolicy import D3RLPyMultiTaskPolicy

# class AutoMPCDynamicsGym(gym.Env):
#     def __init__(self, system):
#         self.system = system
#     @property
#     def action_space(self):
#         return gym.spaces.Box(0, 1, shape=(self.system.ctrl_dim,))
#     def reset(self, seed = None, options = None,):
#         pass

#     def step(self, actions):
#         pass

#     @property
#     def observation_space(self):
#         low = [90]*4+[-15, 22]*11
#         high = [125]*4+[15, 48]*11
#         return gym.spaces.Box(np.array(low), np.array(high))

# class D3RLPyMultiTaskPolicy(ampc.Policy):
#     def __init__(self, system):
#         super().__init__(system)

#     def clone(self):
#         return copy.deepcopy(self)

#     def set_ocp(self, ocp):
#         self.ocp = ocp

#     def load_trained_algo(self, algoName, algoPath):
#         action_scaler = d3rlpy.preprocessing.MinMaxActionScaler(minimum=np.zeros(8), maximum=np.ones(8))
#         if algoName == 'CQL':
#             self.algo = d3rlpy.algos.CQL(action_scaler=action_scaler, use_gpu=False)
#         elif algoName == 'IQL':
#             self.algo = d3rlpy.algos.IQL(action_scaler=action_scaler, use_gpu=False)
#         self.algo.build_with_env(AutoMPCDynamicsGym(self.system))
#         self.algo.load_model(algoPath)

#     def step(self, obs):
#         obs = np.concatenate([obs, self.ocp.cost.goal[-2:]])
#         action = self.algo.predict(obs[None, :])
#         if isinstance(self.algo, d3rlpy.algos.DiscreteCQL):
#             actions = []
#             for i in range(8):
#                 actions.append(action%2)
#                 action = action //2
#             actions = np.array(actions)
#         else:
#             actions = (action>0.5).astype(float)
#         actions = actions.squeeze()
#         return actions

#     def pickle(self, filename):
#         with open(filename, 'wb') as f:
#             pickle.dump(self, f)

class AMPCController(Controller):
    controller_file = "./controller.pkl"

    # CQL
    # controller_file = "../softwater_app_2mod/active_controllers/cql.pkl"

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

    def update_target(self, new_target):
        self.target = new_target
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

    def on_start(self):
        print("Controller Start")

        # targ = [float(self.target[0]), float(self.target[1])]
        # self.ocp.set_cost(
        #     ThresholdCost(
        #         system=self.system, goal=targ,
        #         threshold=1.0, observations=["M10X", "M10Y"]
        #     )
        # )

        # for obs in ['M1-PL', 'M1-PR', 'M2-PL', 'M2-PR']:
        #     self.ocp.set_obs_bound(obs, 97, 118)
        # for ctrl in self.system.controls:
        #     self.ocp.set_ctrl_bound(ctrl, 0, 1)

        # self.mpc.set_ocp(self.ocp)
        # self.mpc.reset()
        # self.mpc.optimizer.optimizer.log_df = pd.DataFrame(columns=['States', 'Ctrls', 'Cost', 'Quad', 'Barrier', 'ActiveBarrier','BarrierHorizon', 'Timeout'])
        # print(self.mpc.optimizer.optimizer.ocp.get_cost()._costs[1].scales)

    def on_end(self):
        # self.mpc.optimizer.optimizer.log_df.to_csv(self.data_dir + '/debug_log.csv')
        print("Controller End")

    def evaluate(self, x, p, angles):
        full_x = np.array(list(p[:4]) + list(x[2:22]))
        # print("the full x")
        # print(x)
        # print(p)
        # print(full_x)
        # print(f'{self.system.observations=}')
        start_time = time.perf_counter()
        u = self.mpc.step(full_x)
        end_time = time.perf_counter()

        self.ampc_dt = (end_time - start_time) * 1000
        self.x_ee = x[-2:]
        self.error = [(self.target[0] - self.x_ee[0]), (self.target[1] - self.x_ee[1])]
        self.rmse = math.sqrt((self.error[0] * self.error[0]) + (self.error[1] * self.error[1]))
        u = [i > 0.5 for i in u]
        return u

controller = AMPCController()


