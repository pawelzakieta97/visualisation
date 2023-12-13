import numpy as np

from transformations import look_at, get_perspective_projection_matrix, get_orthographic_projection_matrix


class MVPControl:

    def __init__(self, width=800, height=480, orthographic=False, *args, **kwargs):
        self.view_matrix = None
        self.projection_matrix = None
        self.position = None
        self.ScreenWidth = width
        self.ScreenHeight = height
        self.pos = np.array([5, 5, 5]).astype(float)
        self.pos = np.array([0, 0, 5]).astype(float)
        self.speed = 10.0
        self.fov = 60
        self.yaw = 0
        self.pitch = 0
        self.orthographic = orthographic
        self.zoom = 1

    def reset_view(self):
        self.pos = np.array([0, 0, 5]).astype(float)
        self.fov = 60
        self.zoom = 1
        self.yaw = 0
        self.pitch = 0

    def get_up_direction(self):
        return np.array([np.sin(self.yaw) * np.sin(self.pitch),
                         np.cos(self.pitch),
                         np.sin(self.pitch) * np.cos(self.yaw)])

    def get_forward_direction(self):
        return np.array([-np.sin(self.yaw) * np.cos(self.pitch),
                         np.sin(self.pitch),
                         -np.cos(self.pitch) * np.cos(self.yaw)])

    def get_right_direction(self):
        return np.array([np.cos(self.yaw),
                         0,
                         -np.sin(self.yaw)])

    def move_forward(self, distance):
        if not self.orthographic:
            self.pos += self.get_forward_direction() * distance

    def move_up(self, distance):
        self.pos += self.get_up_direction() * distance

    def move_right(self, distance):
        self.pos += self.get_right_direction() * distance

    def turn_up(self, angle):
        self.pitch += angle

    def turn_right(self, angle):
        self.yaw += angle

    def resize(self, width=0, height=0):
        self.ScreenWidth = width
        self.ScreenHeight = height

    def get_projection_matrix(self):
        aspect_ratio = self.ScreenWidth / self.ScreenHeight
        if self.orthographic:
            return get_orthographic_projection_matrix(self.zoom, aspect_ratio, far=10000)
        else:
            return get_perspective_projection_matrix(self.fov * np.pi / 180, aspect_ratio=aspect_ratio, zoom=self.zoom)

    def get_view_matrix(self):
        if self.orthographic:
            return look_at(position=self.pos + self.get_forward_direction() * (-1000), target=self.pos)
        return look_at(position=self.pos, yaw=self.yaw, pitch=self.pitch)

    def get_pos(self):
        return self.pos if not self.orthographic else self.pos / np.linalg.norm(self.pos) * 1e6


class MVPController(MVPControl):

    def __init__(self, enable_control=True, *args, **kwargs):
        MVPControl.__init__(self, *args, **kwargs)
        self.mouse_mode = -1
        self.lastX = 0
        self.lastY = 0
        self.enable_control = enable_control

    def on_special_key(self, key, x, y):
        print(key)

    def on_keyboard(self, keyboard_state, dt):
        if not self.enable_control:
            return
        if not keyboard_state:
            return
        speed = self.speed
        if self.orthographic:
            speed /= self.zoom * 3
        if 'w' in keyboard_state:
            if self.orthographic:
                self.move_up(speed * dt)
            else:
                self.move_forward(speed * dt)
        if 's' in keyboard_state:
            if self.orthographic:
                self.move_up(-speed * dt)
            else:
                self.move_forward(-speed * dt)
        if 'a' in keyboard_state:
            self.move_right(-speed * dt)
        if 'd' in keyboard_state:
            self.move_right(speed * dt)
        if 'q' in keyboard_state:
            self.move_up(-speed * dt)
        if 'e' in keyboard_state:
            self.move_up(speed * dt)

    def on_mouse(self, *args, **kwargs):
        if not self.enable_control:
            return
        (key, Up, x, y) = args
        if (key == 0) & (Up == 0):
            self.lastX = x
            self.lastY = y
            self.mouse_mode = 1
        elif (key == 2) & (Up == 0):
            self.lastX = x
            self.lastY = y
            self.mouse_mode = 2
        elif key == 3:
            self.zoom *= 1.1
        elif key == 4:
            self.zoom /= 1.1
        else:
            self.lastX = -1
            self.lastY = -1
            self.mouse_mode = -1
        # print "please overrider on_mousemove" ,args

    def on_mousemove(self, *args, **kwargs):
        if not self.enable_control:
            return
        deltaX = self.lastX - args[0]
        deltaY = self.lastY - args[1]
        if self.mouse_mode == 1:
            (self.lastX, self.lastY) = args
            self.turn_up(deltaY * 0.01)
            self.turn_right(deltaX * 0.01)
        elif self.mouse_mode == 2:
            (self.lastX, self.lastY) = args
        # print "please overrider on_mousemove" ,args
