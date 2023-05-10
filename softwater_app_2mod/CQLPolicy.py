import d3rlpy
import autompc
import numpy as np
import pickle
import gym
import sys
import copy

class AutoMPCDynamicsGym(gym.Env):
    def __init__(self, system):
        self.system = system
    @property
    def action_space(self):
        return gym.spaces.Box(0, 1, shape=(self.system.ctrl_dim,))
    def reset(self, seed = None, options = None,):
        pass

    def step(self, actions):
        pass

    @property
    def observation_space(self):
        low = [90]*4+[-15, 22]*11
        high = [125]*4+[15, 48]*11
        return gym.spaces.Box(np.array(low), np.array(high))

class D3RLPyMultiTaskPolicy(autompc.Policy):
    def __init__(self, system):
        super().__init__(system)

    def clone(self):
        return copy.deepcopy(self)

    def set_ocp(self, ocp):
        self.ocp = ocp

    def load_trained_algo(self, algoName, algoPath):
        action_scaler = d3rlpy.preprocessing.MinMaxActionScaler(minimum=np.zeros(8), maximum=np.ones(8))
        if algoName == 'CQL':
            self.algo = d3rlpy.algos.CQL(action_scaler=action_scaler, use_gpu=False)
        elif algoName == 'IQL':
            self.algo = d3rlpy.algos.IQL(action_scaler=action_scaler, use_gpu=False)
        self.algo.build_with_env(AutoMPCDynamicsGym(self.system))
        self.algo.load_model(algoPath)

    def step(self, obs):
        obs = np.concatenate([obs, self.ocp.cost.goal[-2:]])
        action = self.algo.predict(obs[None, :])
        if isinstance(self.algo, d3rlpy.algos.DiscreteCQL):
            actions = []
            for i in range(8):
                actions.append(action%2)
                action = action //2
            actions = np.array(actions)
        else:
            actions = (action>0.5).astype(float)
        actions = actions.squeeze()
        return actions

    def pickle(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

# if __name__ == '__main__':
#     observations = ["M1-PL", "M1-PR", "M2-PL", "M2-PR"]
#     for i in range(1, 11):
#         observations += [f"M{i}X", f"M{i}Y"]
#     controls = ["M1-AL-IN", "M1-AL-OUT", "M1-AR-IN", "M1-AR-OUT", 
#                 "M2-AL-IN", "M2-AL-OUT", "M2-AR-IN", "M2-AR-OUT"]
#     system = autompc.System(observations, controls, dt=0.5)
#     policy = D3RLPyMultiTaskPolicy(system)
#     policy.load_trained_algo('CQL', '../../../run_softwater_multitask/score_-1968.9770014477122_tau_2.0_actor_lr_0.0001_critic_lr_0.0001_seed_2.pt')
#     policy.pickle('controller.pkl')
#     print('Done pickling')