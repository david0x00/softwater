from controller import Controller
import simple_controller
import visual_servo
import ampc_controller
import numpy as np
import time

class TrajectoryController(Controller):
    def __init__(self):
        super().__init__()
    
    def on_start(self):
        print("Controller Start")
    
    def on_end(self):
        print("Controller End")

    def evaluate(self, x, p, angles):
        u = self.chosencontroller.evaluate(x, p, angles) 
        return u

controller = TrajectoryController()