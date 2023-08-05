from controller import Controller
import numpy as np


class LengthController(Controller):

    def __init__(self):
        super().__init__()
        self.choose_left = False

        self.left_start = 12
        self.right_start = 12

        self.left_end = 15
        self.right_end = 18

        steps = 8
        self.left_sequence = [self.left_start]
        self.right_sequence = [self.right_start]
        for i in range(steps):
            next_left = self.left_start + (((self.left_end - self.left_start) / steps) * (i + 1))
            next_right = self.right_start + (((self.right_end - self.right_start) / steps) * (i + 1))
            self.left_sequence.append(next_left)
            self.right_sequence.append(next_right)
        print(self.left_sequence)
        print(self.right_sequence)

    def on_start(self):
        print("Controller Start")

    def on_end(self):
        print("Controller End")

    # def implement_controls(self, u):
    #     pass

    def rad(self, deg):
        return deg * np.pi/180.0
    
    def new_range(self, x_vals, y_vals, x1, x2, y1, y2):
        x_vals_base = x_vals[0]
        x_vals_end = x_vals[-1]
        y_vals_base = y_vals[0]
        y_vals_end = y_vals[-1]

        x_old_min = min(x_vals_base, x_vals_end)
        x_old_max = max(x_vals_base, x_vals_end)

        y_old_min = min(y_vals_base, y_vals_end)
        y_old_max = max(y_vals_base, y_vals_end)

        x_new_min = min(x1, x2)
        x_new_max = max(x1, x2)

        y_new_min = min(y1, y2)
        y_new_max = max(y1, y2)

        x_old_range = max(x_old_max - x_old_min, 0.2)
        y_old_range = max(y_old_max - y_old_min, 0.2)

        x_new_range = x_new_max - x_new_min
        y_new_range = y_new_max - y_new_min

        x_new = []
        y_new = []
        for i in range(len(x_vals)):
            if x_old_range == 0:
                x = x_new_min
            else:
                x = (((x_vals[i] - x_old_min) * x_new_range) / x_old_range) + x_new_min

            if y_old_range == 0:
                y = y_new_min
            else:
                y = (((y_vals[i] - y_old_min) * y_new_range) / y_old_range) + y_new_min

            x_new.append(x)
            y_new.append(y)
    
        length = 0
        for i in range(1, len(x_vals)):
            x1 = x_new[i - 1]
            y1 = y_new[i - 1] 

            x2 = x_new[i]
            y2 = y_new[i] 

            x_diff = x2 - x1
            y_diff = y2 - y1
            # print(x_diff, y_diff)
            length += np.sqrt((x_diff)**2 + (y_diff)**2)
    
        return x_new, y_new, length

    def get_length(self, x, a):
        base_angle = a[0]
        end_angle = a[1]
        x_vals = x[0::2][:6]
        y_vals = x[1::2][:6]
        # print(base_angle, end_angle)
        # print(x_vals)
        # print(y_vals)

        end_left_x = x_vals[-1] - np.cos(self.rad(end_angle))*4
        end_left_y = y_vals[-1] - np.sin(self.rad(end_angle))*4

        end_right_x = x_vals[-1] + np.cos(self.rad(end_angle))*4
        end_right_y = y_vals[-1] + np.sin(self.rad(end_angle))*4

        base_left_x = x_vals[0] - np.cos(self.rad(base_angle))*4
        base_left_y = y_vals[0] - np.sin(self.rad(base_angle))*4

        base_right_x = x_vals[0] + np.cos(self.rad(base_angle))*4
        base_right_y = y_vals[0] + np.sin(self.rad(base_angle))*4

        _, _, left_length = self.new_range(x_vals, y_vals, end_left_x, base_left_x, end_left_y, base_left_y)
        _, _, right_length = self.new_range(x_vals, y_vals, end_right_x, base_right_x, end_right_y, base_right_y)

        return left_length, right_length
    
    def evaluate(self, *args):
        x = args[0]
        p = args[1]
        a = args[2]
        u = [False for _ in range(len(self.u_headers))]

        left_length, right_length = self.get_length(x, a)
        print(left_length, right_length)

        if self.choose_left and len(self.left_sequence) > 0:
            if left_length < self.left_sequence[0]:
                u[0] = True
            else:
                del self.left_sequence[0]
                self.choose_left = not self.choose_left
        elif self.choose_left == False and len(self.right_sequence) > 0:
            if right_length < self.right_sequence[0]:
                u[2] = True
            else:
                del self.right_sequence[0]
                self.choose_left = not self.choose_left
        return u

controller = LengthController()