from controller import Controller
import simple_controller
import visual_servo
import ampc_controller
import trpo_controller
import manual
import numpy as np
import time
import math

class TrajGenerator:
    def __init__(self):
        pass

    def figure_eight(self, t):
        x = 5*np.sin(t)
        y = 5*np.sin(t)*np.cos(t) + 29
        return x, y

    def length(self, x, y):
        return np.sqrt(np.diff(x)**2 + np.diff(y)**2).sum()

    def generate_equal_length_waypoints(self, num_waypoints):
        t_values = np.linspace(0, 2*np.pi, 1000)
        x, y = self.figure_eight(t_values)
        total_length = self.length(x, y)
        segment_length = total_length / num_waypoints

        waypoints = [(x[0], y[0])]
        current_length = 0
        for i in range(1, len(t_values)):
            segment_len = self.length(x[:i+1], y[:i+1])
            if segment_len >= current_length + segment_length:
                waypoints.append((x[i], y[i]))
                current_length += segment_length
            if len(waypoints) == num_waypoints:
                break
        print('Lengths')
        print(total_length, segment_length)
        return waypoints


class TrajectoryController(Controller):
    num_waypoints = 30
    cycles_before_change = 20

    def __init__(self):
        super().__init__()
        # self.point_controller = trpo_controller.controller
        self.point_controller = ampc_controller.controller
        # self.point_controller = visual_servo.controller
        # self.start_controller = ampc_controller.controller
        # self.start_controller = manual.controller
        traj_generator = TrajGenerator()
        self.waypoints = traj_generator.generate_equal_length_waypoints(self.num_waypoints)
        self.waypoints.append(self.waypoints[0])
        print(self.waypoints)
        self.counter = 0
        self.waypoint_idx = 0
        self.has_started = False

    def extra_headers(self):
        headers = [
            "WAYX",
            "WAYY",
            "XEEX",
            "XEEY",
            "DIST"
        ]
        return headers

    def extra_data(self):
        data = [
            self.curr_waypoint[0],
            self.curr_waypoint[1],
            self.x_ee[0],
            self.x_ee[1],
            self.total_dist
        ]
        return data

    def on_start(self):
        print("Controller Start")
        self.has_started = False
        self.point_controller.on_start()
        self.total_dist = 0
        self.counter = 0
        self.waypoint_idx = 0
        self.curr_waypoint = self.waypoints[self.waypoint_idx]
        print("waypoint " + str(self.waypoint_idx) + ": " + str(self.curr_waypoint))
        self.point_controller.update_target(self.curr_waypoint)

        # self.start_controller.on_start()
        # self.start_controller.update_target(self.curr_waypoint)
    
    def on_end(self):
        print("Controller End")
        self.point_controller.on_end()
    
    def get_distance(self, x, y):
        return math.sqrt((x[0] - y[0])**2 + (x[1] - y[1])**2)

    def evaluate(self, x, p, angles):
        self.x_ee = x[-2:]
        self.total_dist = self.get_distance(self.x_ee, self.curr_waypoint)
        print(f'{self.has_started}')
        print(f'{self.x_ee}')
        print(f'{self.total_dist}')

        if not self.has_started:
            if self.total_dist < 0.5:
                print("Start!")
                self.has_started = True
            else:
                # u = self.start_controller.evaluate(x, p, angles)
                u = self.pressed_valve_state
                u = u[0:4] + u[8:12]
                # print(f'{self.start_controller.mpc.ocp.cost.goal}')
                # print("autompc u: " + str(u))
                return u

        if self.counter == 0:
            self.counter = self.cycles_before_change
            self.waypoint_idx += 1
            self.curr_waypoint = self.waypoints[self.waypoint_idx]
            self.point_controller.update_target(self.curr_waypoint)
            print("waypoint " + str(self.waypoint_idx) + ": " + str(self.curr_waypoint))
        
        u = self.point_controller.evaluate(x, p, angles)
        self.counter -= 1
        return u

controller = TrajectoryController()
