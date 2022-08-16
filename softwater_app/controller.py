import numpy as np
import os
import cv2
import datetime
import csv
import pickle
import queue
import threading
import autompc as ampc
from autompc.costs import ThresholdCost

class Controller:
    emergency_stop = False
    max_pressure_threshold = 119
    run_time = 50
    control_headers = ["TIME", "M1-AL-IN", "M1-AL-OUT", "M1-AR-IN",
                       "M1-AR-OUT", "M2-AL-IN", "M2-AL-OUT", "M2-AR-IN",
                       "M2-AR-OUT", "PUMP", "GATE", "M1-PL", "M1-PR", "M2-PL",
                       "M2-PR", "M1X", "M1Y", "M2X", "M2Y", "M3X", "M3Y",
                       "M4X", "M4Y", "M5X", "M5Y", "M6X", "M6Y", "M7X", "M7Y",
                       "M8X", "M8Y", "M9X", "M9Y", "M10X", "M10Y"]

    def __init__(self):
        self.img_arr = []
        self.obs = np.zeros(24)
        self._in_queue = queue.Queue()
        self._out_queue = queue.Queue()
    
    def check_emergency_stop(self):
        return self.emergency_stop

    def call_emergency_stop(self):
        print("CALLING EMERGENCY STOP")
        self.emergency_stop = True
        #self.robot.return_to_home()

    def reset_emergency_stop(self):
        self.emergency_stop = False

    def write_imgs(self, data_dir):
        print("Writing Images...")
        img_dir = data_dir + "imgs/"
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
        for idx, img in enumerate(self.img_arr):
            file_name = img_dir + str(idx) + ".jpg"
            cv2.imwrite(file_name, img)
        print("Done.")
    
    def pipe_out(self):
        try:
            return self._out_queue.get_nowait()
        except queue.Empty:
            return None
    
    def pipe_in(self, msg):
        self._in_queue.put(msg)

    def get_observations(self):
        self._out_queue.put({'command': {'get keyframe': None}})
        
        keypoints, pvalues = self._in_queue.get()

        for i in range(4):
            self.obs[i] = pvalues[i]

    def implement_controls(self):
        values = []
        for i in self.u:
            values.append(bool(i))
        self._out_queue.put({'command': {'set solenoids': values}})

    def save_control_state(self, st):
        pass
        '''current_time = datetime.datetime.now()
        with open(self.data_file, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.control_headers)

            elapsed_time = round((current_time - st).total_seconds(),3)

            row_dict = {}
            for idx, h in enumerate(self.control_headers):
                if idx == 0:
                    row_dict[h] = elapsed_time
                elif idx > 0 and idx < 9:
                    row_dict[h] = self.u[idx - 1]
                elif idx == 9:
                    row_dict[h] = 1
                elif idx == 10:
                    x = (self.u * self.robot.gate_mask).sum()
                    if x:
                        row_dict[h] = 1
                    else:
                        row_dict[h] = 0
                elif idx >= 11 and idx < 35:
                    row_dict[h] = self.obs[idx - 11]

            writer.writerow(row_dict)'''
    
    def prepare(self):
        self.reset_emergency_stop()
        self.img_arr = []

        #mint = [0, 0, 141]
        #maxt = [141, 137, 255]
        #maxt = [133, 115, 255]
        #color_threshold = (np.array(mint), np.array(maxt))
        #init_img = self.robot.camera.get_opencv_img()
        #self.md = MarkerDetector(init_img, color_threshold)


class SimpleController(Controller):
    controller_file = "./appdata/simple_controller.p"

    def __init__(self):
        super().__init__()
        simple_controller = pickle.load( open( self.controller_file, "rb" ) )
        self.controller = simple_controller["comb"]

    def prepare(self, targ=(9, 27)):
        super().prepare()
        self.pressures = self.controller[targ]
        print(self.pressures)

        self.get_observations()
    
    def evaluate(self, obs):
        u = np.zeros(8)
        for i in range(4):
            if obs[i] < self.pressures[i]:
                u[i*2] = 1
        return u
    
    def run_controller(self):
        start_time = datetime.datetime.now()
        loop_number = -1
        loop_period = 0.5
        timer = self.run_time
        while 1:
            if self.check_emergency_stop():
                break

            curr_time = datetime.datetime.now()
            elapsed_time = (curr_time - start_time).total_seconds()

            if elapsed_time > timer:
                break

            proposed_loop_number = int(elapsed_time / loop_period)
            if proposed_loop_number > loop_number:
                #print(elapsed_time)
                loop_number = proposed_loop_number
                self.get_observations()
                self.u = self.evaluate(self.obs)
                if not self.check_emergency_stop():
                    self.implement_controls()
                self.save_control_state(start_time)
            
        print("Done! Final Dest = (" + str(self.obs[-2]) + ", " + str(self.obs[-1]) + ")")

class ClosedLoopIK(Controller):
    controller_file = "./appdata/simple_controller.p"

    def __init__(self):
        super().__init__()
        simple_controller = pickle.load( open( self.controller_file, "rb" ) )
        self.controller = simple_controller["comb"]

    def prepare(self, targ=(9, 27)):
        super().prepare()
        self.targ = targ
        self.pressures = self.controller[targ]
        print(self.pressures)

        self.Px = 1
        self.Py = 1
        self.Ix = 1
        self.Iy = 1

        self.x_idx = 22
        self.y_idx = 23

        self.err_x_I = 0
        self.err_y_I = 0

        self.control_targ = self.targ

        self.pressure_flags = [False, False, False, False]
        self.change_targ = False

        self.get_observations()
    
    def evaluate(self, obs):
        if self.change_targ:
            targ_x = self.targ[0]
            targ_y = self.targ[1]

            curr_x = self.obs[self.x_idx]
            curr_y = self.obs[self.y_idx]

            err_x = targ_x - curr_x
            err_y = targ_y - curr_y

            self.err_x_I += err_x

            curr_targ_x = self.control_targ[0]

            con_x = curr_targ_x + (err_x * self.Px) + (self.err_x_I * self.Ix)
        
        u = np.zeros(8)
        for i in range(4):
            if obs[i] < self.pressures[i]:
                u[i*2] = 1
        return u

    def run_controller(self):
        start_time = datetime.datetime.now()
        loop_number = -1
        loop_period = 0.5
        timer = self.run_time
        while 1:
            if self.check_emergency_stop():
                break

            curr_time = datetime.datetime.now()
            elapsed_time = (curr_time - start_time).total_seconds()

            if elapsed_time > timer:
                break

            proposed_loop_number = int(elapsed_time / loop_period)
            if proposed_loop_number > loop_number:
                #print(elapsed_time)
                loop_number = proposed_loop_number
                self.get_observations()
                self.u = self.evaluate(self.obs)
                if not self.check_emergency_stop():
                    self.implement_controls()
                self.save_control_state(start_time)
            
        print("Done! Final Dest = (" + str(self.obs[-2]) + ", " + str(self.obs[-1]) + ")")

class AMPCController(Controller):
    # Original
    # controller_file = "/home/pi/Desktop/acc40/controllers/ampc1_comb.pkl"
    # tuner_file = "/home/pi/softwater/application/tune_result_altered.pkl"
    barrier_file = "/home/pi/dohun/underwater_robot_autompc-0.2-dev-fix/experiment_scripts/endtoend_barrier_defaultgoals/controller.pkl"
    quad_file = "/home/pi/dohun/underwater_robot_autompc-0.2-dev-fix/experiment_scripts/endtoend_quad_defaultgoals/controller.pkl"
    controller_file = quad_file
    tuner_file = "/home/pi/Desktop/dohun_test/tune_result.pkl"

    def __init__(self, robot):
        super().__init__(robot)
        with open(self.controller_file, "rb") as f:
            self.controller = pickle.load(f)
        self.system = self.controller.system

    def prepare(self, targ, data_dir):
        super().prepare()

        self.get_observations()

        target = [float(targ[0]), float(targ[1])]
        ocp = ampc.OCP(self.system)
        ocp.set_cost(ThresholdCost(system=self.system, goal=target, threshold=2.0, observations=["M10X", "M10Y"]))
        for ctrl in self.system.controls:
            ocp.set_ctrl_bound(ctrl, 0, 1)
        self.controller.set_ocp(ocp)
        self.controller.reset()

        # create tajectory for history
        traj = ampc.Trajectory.zeros(self.system, 1)
        traj[0].obs[:] = self.obs
        # generate the controller state
        # constate = controller.traj_to_state(traj)
        self.controller.model._device = "cpu"
        print(self.system.observations)
        print(self.system.controls)

        print(targ)
        self.data_file = data_dir + "control_data_" + str(int(targ[0])) + "_" + str(int(targ[1])) + ".csv"
        if os.path.exists(self.data_file):
            print("something wrong!!!")
        with open(self.data_file, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.control_headers)
            writer.writeheader()

    def run_controller(self):
        start_time = datetime.datetime.now()
        loop_number = -1
        loop_period = 0.5
        timer = self.run_time
        while 1:
            if self.check_emergency_stop():
                break

            curr_time = datetime.datetime.now()
            elapsed_time = (curr_time - start_time).total_seconds()

            if elapsed_time > timer:
                break

            proposed_loop_number = int(elapsed_time / loop_period)
            if proposed_loop_number > loop_number:
                #print(elapsed_time)
                loop_number = proposed_loop_number
                self.get_observations()
                self.u = self.controller.step(self.obs)
                if not self.check_emergency_stop():
                    self.implement_controls()
                self.save_control_state(start_time)
            
        self.robot.turn_off_robot()
        print("Done! Final Dest = (" + str(self.obs[-2]) + ", " + str(self.obs[-1]) + ")")


class SimpleControllerThread(SimpleController, threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        SimpleController.__init__(self)

    def run(self):
        self.prepare()
        self.run_controller()
        

