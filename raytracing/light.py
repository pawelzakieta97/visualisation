import numpy as np

class Light:
    def get_light_direction(self, pos: np.array):
        ...

class SunLight(Light):
    def __init__(self, pos=None, color=None):
        if pos is None:
            pos = np.array([-1.0, 0.8, 0.5])
            pos /= np.linalg.norm(pos)
        if color is None:
            color = np.array([1, 0.92, 0.75]) * 8
        self.pos = pos
        self.color = color

    def get_light_direction(self, pos: np.array):
        return self.pos[None, :] * np.ones((pos.shape[0], 1))
