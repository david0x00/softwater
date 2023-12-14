from controller import Controller
import simple_controller
import visual_servo
import ampc_controller
import trpo_controller
import manual
import numpy as np
import time
import math

class Arc:
    num_waypoints = 100

    def __init__(self, left=False, right=False, up=False, down=False):
        if left is True:
            if up is True:
                self.center = (-7, 24)
                xc = 7
                yc = 5
                xf = np.cos
                yf = np.sin
            elif down is True:
                self.center = (0, 29)
                xc = -7
                yc = -5
                xf = np.sin
                yf = np.cos
        if right is True:
            if up is True:
                self.center = (7, 24)
                xc = -7
                yc = 5
                xf = np.cos
                yf = np.sin
            elif down is True:
                self.center = (0, 29)
                xc = 7
                yc = -5
                xf = np.sin
                yf = np.cos
         
        waypoints = []
        for i in range(self.num_waypoints+1):
            angle = np.pi * i / self.num_waypoints / 2
            x = self.center[0] + xc * xf(angle)
            y = self.center[1] + yc * yf(angle)
            waypoints.append((x, y))
        # waypoints.append(waypoints[0])
        self.waypoints = waypoints
    
    def get_waypoints(self):
        return self.waypoints

class HalfTri:
    logo_vertices = np.array([
        [0, 25],
        [4, 29],
        [0, 33]
    ])

    num_waypoints = 100

    def __init__(self):
        # Calculate the total length of the logo's perimeter
        total_logo_length = np.sum(np.linalg.norm(np.diff(self.logo_vertices, axis=0), axis=1))
    
        # Define the number of desired waypoints and calculate the step size
        step_size = total_logo_length / self.num_waypoints
    
        # Generate the waypoints along the perimeter
        self.waypoints = []
        current_distance = 0
        for i in range(len(self.logo_vertices) - 1):
            start = self.logo_vertices[i]
            end = self.logo_vertices[i + 1]
            segment_length = np.linalg.norm(end - start)

            while current_distance + step_size < segment_length:
                t = (current_distance + step_size) / segment_length
                interpolated_point = (1 - t) * start + t * end
                self.waypoints.append(interpolated_point)
                current_distance += step_size

            current_distance -= segment_length

        # Add the last vertex as a waypoint
        self.waypoints.append(self.logo_vertices[-1])

        # Extract x and y coordinates from the waypoints
        self.waypoints = np.array(self.waypoints)
    
    def get_waypoints(self):
        return self.waypoints


class SemiCircle:
    center = (0, 29)
    radius = 4
    num_waypoints = 200

    def __init__(self, left=False, right=False):
        if left == True:
            x_multiplier = -1
        else:
            x_multiplier = 1

        waypoints = []
        for i in range(self.num_waypoints+1):
            angle = np.pi * i / self.num_waypoints
            x = self.center[0] + x_multiplier * self.radius * np.sin(angle)
            y = self.center[1] - self.radius * np.cos(angle)
            waypoints.append((x, y))
        # waypoints.append(waypoints[0])
        self.waypoints = waypoints
    
    def get_waypoints(self):
        return self.waypoints

class Straight:
    logo_vertices = np.array([
        [0, 25],
        [3, 25],
        [3, 27],
        [1.5, 27],
        [1.5, 31],
        [3, 31],
        [3, 33],
        [-3, 33],
        [-3, 31],
        [-1.5, 31],
        [-1.5, 27],
        [-3, 27],
        [-3, 25],
        [0, 25]
    ])

    num_waypoints = 500

    def __init__(self):
        # Calculate the total length of the logo's perimeter
        total_logo_length = np.sum(np.linalg.norm(np.diff(self.logo_vertices, axis=0), axis=1))
    
        # Define the number of desired waypoints and calculate the step size
        step_size = total_logo_length / self.num_waypoints
    
        # Generate the waypoints along the perimeter
        self.waypoints = []
        current_distance = 0
        for i in range(len(self.logo_vertices) - 1):
            start = self.logo_vertices[i]
            end = self.logo_vertices[i + 1]
            segment_length = np.linalg.norm(end - start)

            while current_distance + step_size < segment_length:
                t = (current_distance + step_size) / segment_length
                interpolated_point = (1 - t) * start + t * end
                self.waypoints.append(interpolated_point)
                current_distance += step_size

            current_distance -= segment_length

        # Add the last vertex as a waypoint
        self.waypoints.append(self.logo_vertices[-1])

        # Extract x and y coordinates from the waypoints
        self.waypoints = np.array(self.waypoints)
    
    def get_waypoints(self):
        return self.waypoints

class Circle:
    center = (0, 29)
    radius = 4
    num_waypoints = 300

    def __init__(self):
        waypoints = []
        for i in range(self.num_waypoints):
            angle = 2 * np.pi * i / self.num_waypoints
            x = self.center[0] - self.radius * np.sin(angle)
            y = self.center[1] - self.radius * np.cos(angle)
            waypoints.append((x, y))
        waypoints.append(waypoints[0])
        self.waypoints = waypoints
    
    def get_waypoints(self):
        return self.waypoints

class BlockI:
    logo_vertices = np.array([
        [0, 25],
        [3, 25],
        [3, 27],
        [1.5, 27],
        [1.5, 31],
        [3, 31],
        [3, 33],
        [-3, 33],
        [-3, 31],
        [-1.5, 31],
        [-1.5, 27],
        [-3, 27],
        [-3, 25],
        [0, 25]
    ])

    num_waypoints = 500

    def __init__(self):
        # Calculate the total length of the logo's perimeter
        total_logo_length = np.sum(np.linalg.norm(np.diff(self.logo_vertices, axis=0), axis=1))
    
        # Define the number of desired waypoints and calculate the step size
        step_size = total_logo_length / self.num_waypoints
    
        # Generate the waypoints along the perimeter
        self.waypoints = []
        current_distance = 0
        for i in range(len(self.logo_vertices) - 1):
            start = self.logo_vertices[i]
            end = self.logo_vertices[i + 1]
            segment_length = np.linalg.norm(end - start)

            while current_distance + step_size < segment_length:
                t = (current_distance + step_size) / segment_length
                interpolated_point = (1 - t) * start + t * end
                self.waypoints.append(interpolated_point)
                current_distance += step_size

            current_distance -= segment_length

        # Add the last vertex as a waypoint
        self.waypoints.append(self.logo_vertices[-1])

        # Extract x and y coordinates from the waypoints
        self.waypoints = np.array(self.waypoints)
    
    def get_waypoints(self):
        return self.waypoints


class TrajGenerator:
    def __init__(self):
        pass

    def figure_eight(self, t):
        # Top Right First
        x = 5*np.sin(t)
        y = 5*np.sin(t)*np.cos(t) + 30

        # Top Left First
        # x = -1*5*np.sin(t)
        # y = 5*np.sin(t)*np.cos(t) + 29

        # Bot Left First
        # x = -1*5*np.sin(t)
        # y = -1*5*np.sin(t)*np.cos(t) + 29

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
    num_waypoints = 500
    cycles_before_change = 20

    def __init__(self):
        super().__init__()
        self.timing_data = [[],[],[]]
        # self.point_controller = trpo_controller.controller
        # self.point_controller = ampc_controller.controller
        # self.point_controller = visual_servo.controller
        self.point_controller = simple_controller.controller
        # self.start_controller = ampc_controller.controller
        # self.start_controller = manual.controller
        # self.start_controller = manual.controller

        # traj_generator = TrajGenerator()
        # self.waypoints = traj_generator.generate_equal_length_waypoints(self.num_waypoints)
        # self.waypoints.append(self.waypoints[0])

        # self.waypoints = BlockI().get_waypoints()

        # self.waypoints = Circle().get_waypoints()
        # self.waypoints = SemiCircle().get_waypoints()
        # self.waypoints = HalfTri().get_waypoints()
        self.waypoints = Arc(right=True, up=True).get_waypoints()

        # print(self.waypoints)
        self.counter = 0
        self.waypoint_idx = 0
        self.has_started = False

    def extra_headers(self):
        headers = [
            "WAYX",
            "WAYY",
            "XEEX",
            "XEEY",
            "DIST",
            # "TARGX", # Visual servo Start
            # "TARGY"
            # "ERRORX",
            # "ERRORY",
            # "DT",
            # "INT_ERRX",
            # "INT_ERRY",
            # "PX",
            # "PY",
            # "IX",
            # "IY",
            # "ADJ_TARGX",
            # "ADJ_TARGY",
            # "TP1L",
            # "TP1R",
            # "TP2L",
            # "TP2R",
            # "KPX",
            # "KPY",
            # "KIX",
            # "KIY" # visual servo end
        ]
        return headers

    def extra_data(self):
        data = [
            self.curr_waypoint[0],
            self.curr_waypoint[1],
            self.x_ee[0],
            self.x_ee[1],
            self.total_dist,
            # self.point_controller.target[0], # Visual servo start
            # self.point_controller.target[1]
            # self.point_controller.error[0][0],
            # self.point_controller.error[1][0],
            # self.point_controller.dt,
            # self.point_controller.integration_error[0][0],
            # self.point_controller.integration_error[1][0],
            # self.point_controller.P[0][0],
            # self.point_controller.P[1][0],
            # self.point_controller.I[0][0],
            # self.point_controller.I[1][0],
            # self.point_controller.adjusted_target[0],
            # self.point_controller.adjusted_target[1],
            # self.point_controller.target_pressures[0],
            # self.point_controller.target_pressures[1],
            # self.point_controller.target_pressures[2],
            # self.point_controller.target_pressures[3],
            # self.point_controller.Kp[0][0],
            # self.point_controller.Kp[1][0],
            # self.point_controller.Ki[0][0],
            # self.point_controller.Ki[1][0] # visual servo end
        ]
        return data

    def on_start(self):
        print("Controller Start")
        self.has_started = False
        # self.point_controller.on_start()
        self.total_dist = 0
        self.counter = 0
        self.waypoint_idx = 0
        self.curr_waypoint = self.waypoints[self.waypoint_idx]
        print("waypoint " + str(self.waypoint_idx) + ": " + str(self.curr_waypoint))

        visual_servo.controller.on_start()
        self.point_controller.set_ik(visual_servo.controller.ik)

        self.point_controller.update_target(self.curr_waypoint)
        self.point_controller.on_start()
        # self.start_controller.on_start()
        # self.start_controller.update_target(self.curr_waypoint)
    
    def on_end(self):
        print("Controller End")
        self.point_controller.on_end()

        ave_total = sum(self.timing_data[0]) / len(self.timing_data[0])
        update_total = sum(self.timing_data[1]) / len(self.timing_data[1])
        eval_total = sum(self.timing_data[2]) / len(self.timing_data[2])

        print("TIMING DATA")
        print("Total Time: " + str(ave_total))
        print(self.timing_data[0])
        print("Update Time: " + str(update_total))
        print(self.timing_data[1])
        print("Eval Time: " + str(eval_total))
        print(self.timing_data[2])
    
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
                # self.point_controller.set_time() # for visual servo
                self.has_started = True
            else:
                # u = self.start_controller.evaluate(x, p, angles)
                u = self.pressed_valve_state
                u = u[0:4] + u[8:12]
                # print(f'{self.start_controller.mpc.ocp.cost.goal}')
                # print("autompc u: " + str(u))
                return u

        # if self.counter == 0:
        #     self.counter = self.cycles_before_change
        #     self.waypoint_idx += 1
        #     self.curr_waypoint = self.waypoints[self.waypoint_idx]
        #     self.point_controller.update_target(self.curr_waypoint)
        #     print("waypoint " + str(self.waypoint_idx) + ": " + str(self.curr_waypoint))
        
        if self.waypoint_idx < (len(self.waypoints) - 1):
            self.waypoint_idx += 1
            self.curr_waypoint = self.waypoints[self.waypoint_idx]
            start_time = time.time()
            self.point_controller.update_target(self.curr_waypoint)
            update_time_marker = time.time()
            u = self.point_controller.evaluate(x, p, angles)
            eval_time_marker = time.time()
            total_time = eval_time_marker - start_time
            update_time = update_time_marker - start_time
            eval_time = eval_time_marker - update_time_marker
            self.timing_data[0].append(total_time)
            self.timing_data[1].append(update_time)
            self.timing_data[2].append(eval_time)
            print(eval_time)
            
            # self.counter -= 1
            return u
        else:
            print("Done")
            u = self.point_controller.evaluate(x, p, angles)
            return u

controller = TrajectoryController()
