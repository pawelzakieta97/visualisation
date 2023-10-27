import numpy as np

from transformations import look_at, get_projection_matrix


class MVPControl:

    def __init__(self, width=800, height=480, *args, **kwargs):
        self.view_matrix = None
        self.projection_matrix = None
        self.position = None
        self.ScreenWidth = width
        self.ScreenHeight = height
        self.pos = np.array([5, 5, 5]).astype(float)
        self.speed = 10.0
        self.fov = 60
        self.yaw = 0
        self.pitch = 0
        self.update_transformation()

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
        self.pos += self.get_forward_direction() * distance
        self.update_transformation()

    def move_up(self, distance):
        self.pos += self.get_up_direction() * distance
        self.update_transformation()

    def move_right(self, distance):
        self.pos += self.get_right_direction() * distance
        self.update_transformation()

    def turn_up(self, angle):
        self.pitch += angle
        self.update_transformation()

    def turn_right(self, angle):
        self.yaw += angle
        self.update_transformation()

        self.update_transformation()

    def update_transformation(self):
        self.projection_matrix = get_projection_matrix(self.fov * np.pi / 180,
                                                       aspect_ratio=self.ScreenWidth / self.ScreenHeight)
        self.view_matrix = look_at(position=self.pos, yaw=self.yaw, pitch=self.pitch)

    def resize(self, width=0, height=0):
        self.ScreenWidth = width
        self.ScreenHeight = height
        self.update_transformation()

    def get_VP(self):
        return self.projection_matrix @ np.linalg.inv(self.view_matrix)


class MVPController(MVPControl):

    def __init__(self, update_callback, *args, **kwargs):
        self.updateCallback = lambda: None
        MVPControl.__init__(self, *args, **kwargs)
        self.mouse_mode = -1
        self.lastX = 0
        self.lastY = 0

    def on_special_key(self, key, x, y):
        print(key)
        _key = key
        if _key == 104:  # page down
            self.updateCallback()
        elif _key == 105:
            self.updateCallback()
        elif _key == 101:  # up
            self.updateCallback()
        elif _key == 103:  # down
            self.updateCallback()
        elif _key == 102:  # right
            self.updateCallback()
        elif _key == 100:  # left
            self.updateCallback()

    def on_keyboard(self, keyboard_state, dt):
        if not keyboard_state:
            return
        if 'w' in keyboard_state:
            self.move_forward(self.speed * dt)
            self.updateCallback()
        if 's' in keyboard_state:
            self.move_forward(-self.speed * dt)
            self.updateCallback()
        if 'a' in keyboard_state:
            self.move_right(-self.speed * dt)
            self.updateCallback()
        if 'd' in keyboard_state:
            self.move_right(self.speed * dt)
            self.updateCallback()
        if 'q' in keyboard_state:
            self.move_up(-self.speed * dt)
            self.updateCallback()
        if 'e' in keyboard_state:
            self.move_up(self.speed * dt)
            self.updateCallback()

    def on_mouse(self, *args, **kwargs):
        (key, Up, x, y) = args
        if (key == 0) & (Up == 0):
            self.lastX = x
            self.lastY = y
            self.mouse_mode = 1
        elif (key == 2) & (Up == 0):
            self.lastX = x
            self.lastY = y
            self.mouse_mode = 2

        else:
            self.lastX = -1
            self.lastY = -1
            self.mouse_mode = -1
        # print "please overrider on_mousemove" ,args

    def on_mousemove(self, *args, **kwargs):
        deltaX = self.lastX - args[0]
        deltaY = self.lastY - args[1]
        if self.mouse_mode == 1:
            (self.lastX, self.lastY) = args
            self.turn_up(deltaY * 0.01)
            self.turn_right(deltaX * 0.01)
            self.updateCallback()
        elif self.mouse_mode == 2:
            (self.lastX, self.lastY) = args
            # self.lookUpward(deltaY*0.01)
            # print "."
            self.updateCallback()
        # print "please overrider on_mousemove" ,args
