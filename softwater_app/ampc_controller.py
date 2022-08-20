from controller import Controller
import pickle
import autompc as ampc
from autompc.costs import ThresholdCost
import time


class AMPCController(Controller):
    controller_file = "./controller.pkl"

    def __init__(self):
        super().__init__()
        with open(self.controller_file, "rb") as f:
            self.mpc = pickle.load(f)
        self.system = self.mpc.system
        self.ocp = ampc.OCP(self.system)
        self.mpc.model._device = "cuda"

    def on_start(self):
        print("Controller Start")

        targ = [float(self.target[0]), float(self.target[1])]
        self.ocp.set_cost(
            ThresholdCost(
                system=self.system, goal=targ,
                threshold=2.0, observations=["M10X", "M10Y"]
            )
        )
        for ctrl in self.system.controls:
            self.ocp.set_ctrl_bound(ctrl, 0, 1)
        self.mpc.set_ocp(self.ocp)
        self.mpc.reset()

    def on_end(self):
        print("Controller End")

    def evaluate(self, x):
        start = time.time()
        u = self.mpc.step(x)
        print(time.time() - start)
        return list(u)

controller = AMPCController()


