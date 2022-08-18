import numpy as np
import time
import pickle
import datetime
import os
import csv
import cv2
import autompc as ampc
from autompc.costs import ThresholdCost
from markerdetector import MarkerDetector

class Acc40Manager:
    directory = "/home/pi/Desktop/acc40/"
    ampc_comb_dir = "ampc_comb_bc_horizon/"
    # ampc_comb_dir = "ampc_comb/"
    simple_comb_dir = "simple_comb/"
    run_limit = 10
    xc = [[-9,-7,-5,-3,-1,1,3,5,7,9],
          [-9,-7,-5,-3,-1,1,3,5,7,9],
          [-7,-5,-3,-1,1,3,5,7],
          [-5,-3,-1,1,3,5],
          [-3,-1,1,3],
          [-1,1]]
    yc = 25

    def __init__(self, robot):
        self.robot = robot
        self.idx_coords = []
        for i, row in enumerate(self.xc):
            for x in row:
                y = self.yc + i*2
                self.idx_coords.append((x,y))
        
        self.simple_controller = SimpleController(self.robot)
        self.ampc_controller = AMPCController(self.robot)

    def run_simple(self, idx):
        data_directory = self.get_idx_directory(idx) + self.simple_comb_dir
        print(data_directory)
        if not os.path.exists(data_directory):
            os.makedirs(data_directory)
        run_directory = self.get_run_directory(data_directory)

        targ = self.convert_idx(idx)
        self.turn_off()
        self.simple_controller.prepare(targ, run_directory)
        self.simple_controller.run_controller()
        self.simple_controller.write_imgs(run_directory)
        self.return_home()

    def run_ampc(self, idx):
        data_directory = self.get_idx_directory(idx) + self.ampc_comb_dir
        print(data_directory)
        if not os.path.exists(data_directory):
            os.makedirs(data_directory)
        run_directory = self.get_run_directory(data_directory)

        targ = self.convert_idx(idx)
        self.turn_off()
        self.ampc_controller.prepare(targ, run_directory)
        self.ampc_controller.run_controller()
        self.ampc_controller.write_imgs(run_directory)
        self.return_home()
    
    def turn_off(self):
        self.robot.turn_off_robot()

    def return_home(self):
        self.robot.return_to_home()
    
    def get_run_directory(self, directory):
        for i in range(self.run_limit):
            if i == self.run_limit-1:
                print("max runs")
                return None
            ret = directory + "run" + str(i) + "/"
            if not os.path.exists(ret):
                os.makedirs(ret)
                return ret
        return None

    def get_idx_directory(self, idx):
        ret = self.directory + str(idx) + "/"
        if os.path.exists(ret):
            return ret
        else:
            os.makedirs(ret)
        return ret

    def convert_idx(self, idx):
        ret = self.idx_coords[idx]
        print("Coordinates: " + str(ret))
        return ret


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

    def __init__(self, robot):
        self.robot = robot
        self.img_arr = []
        self.obs = np.zeros(24)
    
    def check_emergency_stop(self):
        return self.emergency_stop

    def call_emergency_stop(self):
        print("CALLING EMERGENCY STOP")
        self.emergency_stop = True
        self.robot.return_to_home()

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

    def get_observations(self):
        img = self.robot.camera.get_opencv_img()
        self.img_arr.append(img)

        init_markers = self.md.analyze_threshold_fast(img)
        if init_markers == None:
            self.call_emergency_stop()
            print("Lost Marker Track")
            return
        marker_keys = list(init_markers.keys())

        for i in range(4):
            pread = round(self.robot.pressure_sensors[i].read_sensor(), 3)
            if pread < 130.0:
                self.obs[i] = pread
            else:
                print("Faulty pressure reading " + str(self.obs[i]))
                self.obs[i] = round(self.robot.pressure_sensors[i].read_sensor(), 3)
            if self.obs[i] >= self.max_pressure_threshold:
                print("Max Pressure Exceeded")
                self.call_emergency_stop()
            elif self.obs[i] >= self.max_pressure_threshold - 4:
                print("Pressure close: " + str(self.obs[i]))

        for i in range(1, 11):
            key1 = marker_keys[i*3]
            key2 = marker_keys[i*3 + 1]
            self.obs[(i - 1)*2 + 4] = init_markers[key1]
            self.obs[(i - 1)*2 + 5] = init_markers[key2]

    def implement_controls(self):
        #print(self.u)
        if self.emergency_stop:
            return 

        self.robot.set_pump(True)

        x = (self.u * self.robot.gate_mask).sum()
        if x:
            self.robot.set_gate_valve(True)
        else:
            self.robot.set_gate_valve(False)

        for i in range(len(self.u)):
            u_val = bool(self.u[i])
            self.robot.set_solenoid(i, u_val)

    def save_control_state(self, st):
        current_time = datetime.datetime.now()
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

            writer.writerow(row_dict)
    
    def prepare(self):
        self.reset_emergency_stop()
        self.img_arr = []

        mint = [0, 0, 141]
        #maxt = [141, 137, 255]
        maxt = [133, 115, 255]
        color_threshold = (np.array(mint), np.array(maxt))
        init_img = self.robot.camera.get_opencv_img()
        self.md = MarkerDetector(init_img, color_threshold)

class ClosedLoopIK(Controller):
    model_file = "/Volumes/Flash/comb_bmodel/"

    xmin = -15
    xmax = 15
    ymin = 0
    ymax = 40

    pmin = 95
    pmax = 121

    def rescale(self, p_list):
        ret = []
        for p in p_list:
            ret.append((p * (pmax - pmin)) + pmin)
        return ret

    def normalize(self, x, y):
        ret = np.zeros(2)
        ret[0] = (x - self.xmin) / (self.xmax - self.xmin)
        ret[1] = (y - self.ymin) / (self.ymax - self.ymin)
        ret = ret.reshape(1,-1)
        return ret
        
    def calc_pressures(self, x, y):
        x_in = self.normalize(x, y)
        comb_pred = self.ik_model.predict(x_in)
        comb_final = self.rescale(list(comb_pred[0]))
        return comb_final

    def __init__(self, robot):
        super().__init__(robot)
        self.ik_model = keras.models.load_model(self.model_file)

    def prepare(self, targ, data_dir):
        super().prepare()

        # Get initial pressures
        ip = self.calc_pressures(targ[0], targ[1])


    def run_controller(self):
        # in a loop
        # calculate the error in the cartesian space.
        # 
        pass

class SimpleController(Controller):
    controller_file = "/home/pi/Desktop/acc40/controllers/simple1_comb.p"

    def __init__(self, robot):
        super().__init__(robot)
        simple_controller = pickle.load( open( self.controller_file, "rb" ) )
        self.controller = simple_controller["comb"]

    def prepare(self, targ, data_dir):
        super().prepare()
        self.pressures = self.controller[targ]
        print(self.pressures)

        self.get_observations()

        print(targ)
        self.data_file = data_dir + "control_data_" + str(int(targ[0])) + "_" + str(int(targ[1])) + ".csv"
        if os.path.exists(self.data_file):
            print("something wrong!!!")
        with open(self.data_file, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.control_headers)
            writer.writeheader()
    
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

        self.robot.turn_off_robot()
        print("Done! Final Dest = (" + str(self.obs[-2]) + ", " + str(self.obs[-1]) + ")")


class AMPCController(Controller):
    # Original
    # controller_file = "/home/pi/Desktop/acc40/controllers/ampc1_comb.pkl"
    # tuner_file = "/home/pi/softwater/application/tune_result_altered.pkl"
    # controller_file = "/home/pi/Desktop/dohun_test/controller.pkl"
    tuner_file = "/home/pi/Desktop/dohun_test/tune_result.pkl"
    #controller_file = "/home/pi/dohun/underwater_robot_autompc/experiment_scripts/0808_endtoend_upperlowerbarrier_defaultgoals_200/controller.pkl"
    controller_file = '/home/pi/dohun/underwater_robot_autompc/experiment_scripts/Timeout_TuneIters200_TuneModeendtoend,_TuneGoals10_TuneMetriccost_Costbarrier_Ctrlfreq1/controller.pkl'

    def __init__(self, robot):
        super().__init__(robot)
        with open(self.controller_file, "rb") as f:
            self.controller = pickle.load(f)
        #************** altering the tune
        # with open(self.tuner_file, "rb") as f:
        #     self.tune_result = pickle.load(f)
        # config = self.controller.get_config()
        # config["SumTransformer:_sum_0:M2-AR-OUT_R"] = 1
        # config["SumTransformer:_sum_0:M2-AR-IN_R"] = 1
        # config["SumTransformer:_sum_0:M2-AL-OUT_R"] = 1
        # config["SumTransformer:_sum_0:M2-AL-IN_R"] = 1
        # config["SumTransformer:_sum_0:M1-AR-OUT_R"] = 1
        # config["SumTransformer:_sum_0:M1-AR-IN_R"] = 1
        # config["SumTransformer:_sum_0:M1-AL-OUT_R"] = 1
        # config["SumTransformer:_sum_0:M1-AL-IN_R"] = 1
        # self.controller.set_config(config)
        # self.controller.reset()
        # print(self.controller.optimizer.optimizer.ocp.get_cost()._costs[0]._R)
        #****************************************

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
        print(data_dir)
        self.data_file = data_dir + "control_data_" + str(int(targ[0])) + "_" + str(int(targ[1])) + ".csv"
        if os.path.exists(self.data_file):
            print("something wrong!!!")
        with open(self.data_file, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.control_headers)
            writer.writeheader()

    def run_controller(self):
        import pandas as pd
        self.controller.optimizer.optimizer.df = pd.DataFrame([],columns=['Obs','States','Ctrl','Cost'])
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
                start = time.time()
                self.get_observations()
                obs_time = (time.time() - start ) * 1000
                self.u = self.controller.step(self.obs)
                ampc_time = (time.time() - start ) * 1000 - (obs_time)
                if not self.check_emergency_stop():
                    self.implement_controls()
                imp_time = (time.time() - start ) * 1000 - (ampc_time + obs_time)
                self.save_control_state(start_time)
                save_time = (time.time() - start ) * 1000 - (imp_time + ampc_time + obs_time)
                total_time = (time.time() - start ) * 1000

                print(obs_time, ampc_time, imp_time, save_time, total_time)
            
        self.robot.turn_off_robot()
        self.controller.optimizer.optimizer.df.to_csv(f"/home/pi/dohun/horizon_debug/{time.time()}.csv")
        print("Done! Final Dest = (" + str(self.obs[-2]) + ", " + str(self.obs[-1]) + ")")
    


