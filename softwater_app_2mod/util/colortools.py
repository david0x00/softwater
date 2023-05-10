import math
import numpy as np

from kivy.graphics.texture import Texture


POS_TOP_LEFT = 0
POS_TOP_CENTER = 1
POS_TOP_RIGHT = 2
POS_LEFT = 3
POS_CENTER = 4
POS_RIGHT = 5
POS_BOT_LEFT = 6
POS_BOT_CENTER = 7
POS_BOT_RIGHT = 8


class ColorComponent:
    def __init__(self, c1, c2=None, c1pos=POS_LEFT, c2pos=POS_RIGHT, txtsize=8):
        self.c1 = c1
        self.c2 = c2

        self.txtsize = txtsize
        if c2 is None:
            self.txtsize = 1
            self.cgrad = CGrad(c1, c1, c1pos, c2pos)
            self.texture = self._get_gradient_texture()
        else:
            self.cgrad = CGrad(c1, c2, c1pos, c2pos)
            self.texture = self._get_gradient_texture()

        self.c1pos = self.cgrad.c1pos
        self.c2pos = self.cgrad.c2pos

    def _get_gradient_texture(self):
        texture = Texture.create(size=(self.txtsize, self.txtsize))
        texture.blit_buffer(self.cgrad.to_buffer(self.txtsize), bufferfmt='ubyte', colorfmt='rgb')
        return texture

    def rotate(self, deg):
        s = math.sin(math.radians(deg))
        c = math.cos(math.radians(deg))

        ox = self.c1pos[0] - 0.5
        oy = self.c1pos[1] - 0.5
        self.c1pos[0] = ox * c - oy * s + 0.5
        self.c1pos[1] = ox * s + oy * c + 0.5
        if self.c2 is not None:
            ox = self.c2pos[0] - 0.5
            oy = self.c2pos[1] - 0.5
            self.c2pos[0] = ox * c - oy * s + 0.5
            self.c2pos[1] = ox * s + oy * c + 0.5
        self.update_texture()

    def update_texture(self):
        self.cgrad.move_c1(self.c1pos)
        if self.c2 is None:
            self.txtsize = 1
            self.texture = self._get_gradient_texture()
        else:
            self.cgrad.move_c2(self.c2pos)
            self.texture = self._get_gradient_texture()


class CGrad:
    def __init__(self, c1, c2, c1pos, c2pos):
        self.c1 = c1
        self.c2 = c2
        if type(c1pos) == int:
            self.c1pos = self._find_pos(c1pos)
        else:
            self.c1pos = c1pos
        if type(c2pos) == int:
            self.c2pos = self._find_pos(c2pos)
        else:
            self.c2pos = c2pos

        self.cdiff = self.c1 - self.c2
        self.cdist = self._distance(self.c1pos, self.c2pos)

    def move_c1(self, pos):
        if type(pos) == int:
            self.c1pos = self._find_pos(pos)
        else:
            self.c1pos = pos
        self.cdist = self._distance(self.c1pos, self.c2pos)

    def move_c2(self, pos):
        if type(pos) == int:
            self.c2pos = self._find_pos(pos)
        else:
            self.c2pos = pos
        self.cdist = self._distance(self.c1pos, self.c2pos)

    def color_at(self, pos):
        c1_dist = self._distance(self.c1pos, pos)
        c2_dist = self._distance(self.c2pos, pos)

        if c1_dist == 0:
            return self.c1
        elif c2_dist == 0:
            return self.c2

        temp = (c1_dist ** 2 + self.cdist ** 2 - c2_dist ** 2) / (2 * c1_dist * self.cdist)
        temp = min(temp, 1)
        temp = max(temp, -1)
        angle_c1 = math.degrees(math.acos(temp))
        temp = (self.cdist ** 2 + c2_dist ** 2 - c1_dist ** 2) / (2 * c2_dist * self.cdist)
        temp = min(temp, 1)
        temp = max(temp, -1)
        angle_c2 = math.degrees(math.acos(temp))

        if angle_c1 >= 90:
            return self.c1
        elif angle_c2 >= 90:
            return self.c2

        s = (c1_dist + c2_dist + self.cdist) / 2
        a = math.sqrt(max(s * (s - c1_dist) * (s - c2_dist) * (s - self.cdist), 0))
        h = 2 * a / self.cdist

        dist = math.sqrt(max(c2_dist ** 2 - h ** 2, 0))
        offset = dist / self.cdist

        r = self.cdiff.r * offset + self.c2.r
        g = self.cdiff.g * offset + self.c2.g
        b = self.cdiff.b * offset + self.c2.b
        c = Color(r, g, b)
        return c

    def to_buffer(self, side_len):
        arr = np.ndarray(shape=[side_len, side_len, 3], dtype=np.uint8)
        for y in range(side_len):
            for x in range(side_len):
                if side_len > 1:
                    c = self.color_at((y / (side_len - 1), x / (side_len - 1)))
                else:
                    c = self.color_at((0, 0))
                arr[x, y, 0] = int(c.r)
                arr[x, y, 1] = int(c.g)
                arr[x, y, 2] = int(c.b)
        return np.flipud(arr).tobytes()

    def _distance(self, p1, p2):
        return math.sqrt(pow(p2[0] - p1[0], 2) + pow(p2[1] - p1[1], 2))

    def _find_pos(self, pos):
        if pos == POS_TOP_LEFT:
            return [0, 1]
        elif pos == POS_TOP_CENTER:
            return [0.5, 1]
        elif pos == POS_TOP_RIGHT:
            return [1, 1]
        elif pos == POS_LEFT:
            return [0, 0.5]
        elif pos == POS_CENTER:
            return [0.5, 0.5]
        elif pos == POS_RIGHT:
            return [1, 0.5]
        elif pos == POS_BOT_LEFT:
            return [0, 0]
        elif pos == POS_BOT_CENTER:
            return [0.5, 0]
        return [1, 0]


class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def rgb(self):
        return (self.r, self.g, self.b)

    def bgr(self):
        return (self.b, self.g, self.r)

    def __sub__(self, other):
        return Color(self.r - other.r, self.g - other.g, self.b - other.b)

    def __str__(self):
        return f"RGB: {self.r},{self.g},{self.b}"
