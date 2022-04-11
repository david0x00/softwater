import numpy as np
import pickle
import datetime
from markerdetector import MarkerDetector

class Acc40Manager:
    directory = "/media/pi/Flash/acc40/"
    xc = [[-9,-7,-5,-3,-1,1,3,5,7,9],
          [-9,-7,-5,-3,-1,1,3,5,7,9],
          [-7,-5,-3,-1,1,3,5,7],
          [-5,-3,-1,1,3,5],
          [-3,-1,1,3],
          [-1,1]]
    yc = 25

    def __init__(self):
        self.idx_coords = []
        for i, row in enumerate(self.xc):
            for x in row:
                y = self.yc + i*2
                self.idx_coords.append((x,y))

    def run_simple(self, idx):
        pass

    def run_ampc(self, idx):
        pass

    def return_home(self):
        pass

    def convert_idx(self, idx):
        ret = self.idx_coords[idx]
        print("Coordinates: " + str(ret))
        return ret


class Controller:
    emergency_stop = False
    self.max_pressure_threshold = 19

    def __init__(self, robot):
        self.robot = robot
    
    def check_emergency_stop(self):
        return self.emergency_stop

    def call_emergency_stop(self):
        self.emergency_stop = True
        self.robot.return_to_home()

    def reset_emergency_stop(self):
        self.emergency_stop = False

class SimpleController(Controller):
    controller_file = "/Volumes/Flash/controllers/simple_controller.p"

    def __init__(self, robot):
        super().__init__(robot)
        simple_controller = pickle.load( open( self.controller_file, "rb" ) )
        self.controller = simple_controller["comb"]

    def prepare(self, targ):
        pressures = self.controller[targ]
    
    def run_controller(self):
        pass


class AMPCController(Controller):
    controller_file = "/Volumes/Flash/controllers/ampc_controller_comb.pkl"

    def __init__(self, robot):
        super().__init__(robot)
        with open(self.controller_file_comb, "rb") as f:
            self.controller = pickle.load(f)
        self.system = self.controller.system

    def prepare(self, targ):
        self.reset_emergency_stop()
        mint = [0, 0, 141]
        maxt = [133, 115, 255]
        color_threshold = (np.array(mint), np.array(maxt))
        init_img = self.robot.camera.get_opencv_img()
        self.md = MarkerDetector(init_img, color_threshold)

        self.obs = np.zeros(24)
        self.get_observations()

        target = [float(targ[0]), float(targ[1])]
        ocp = ampc.OCP(self.system)
        ocp.set_cost(ThresholdCost(system=self.system, goal=target, threshold=2.0, observations=["M10X", "M10Y"]))
        for ctrl in self.system.controls:
            ocp.set_ctrl_bound(ctrl, 0, 1)
        self.controller.set_ocp(ocp)
        self.controller.reset()

        # create tajectory for history
        traj = ampc.zeros(self.system, 1)
        traj[0].obs[:] = self.obs
        # generate the controller state
        # constate = controller.traj_to_state(traj)
        self.controller.model._device = "cpu"
        print(self.system.observations)
        print(self.system.controls)

        self.fname = "data/controltarg_" + str(int(target[0]))+ "_" + str(int(target[1])) + ".csv"
        try:
            os.remove(self.fname)
        except:
            pass
        with open(self.fname, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.control_headers)
            writer.writeheader()

    def run_controller(self, controller):
        start_time = datetime.datetime.now()
        loop_number = -1
        loop_period = 0.5
        timer = 50
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
                self.u = self.controller.run(self.obs)
                if not self.check_emergency_stop():
                    self.robot.implement_controls()
                self.save_control_state(start_time)
            
        self.robot.turn_off_robot()
        print("Done!")

    def get_observations(self):
        img = self.robot.camera.get_opencv_img()

        init_markers = self.md.analyze_threshold_fast(img)
        marker_keys = list(init_markers.keys())

        for i in range(4):
            self.obs[i] = round(self.robot.pressure_sensors[i].read_sensor(), 3)
            if self.obs[i] >= self.max_pressure_threshold:
                self.call_emergency_stop()

        for i in range(1, 11):
            key1 = marker_keys[i*3]
            key2 = marker_keys[i*3 + 1]
            self.obs[(i - 1)*2 + 4] = init_markers[key1]
            self.obs[(i - 1)*2 + 5] = init_markers[key2]

    def implement_controls(self):
        #print(self.u)
        self.robot.set_pump(True)

        x = (self.u * self.robot.gate_mask).sum()
        if x:
            self.robot.set_gate_valve(True)
        else:
            self.robot.set_gate_valve(False)

        for i in range(len(self.u)):
            u_val = bool(self.u[i])
            self.robot.set_solenoid(i, u_val)
