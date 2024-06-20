import numpy as np

from raytracing.renderable import Renderable
from models.primitives.sphere import Sphere as SphereMesh


class Sphere(Renderable):
    def __init__(self, pos: np.array = None, radius: float = 1):
        if pos is None:
            pos = np.zeros(3)
        self.pos = pos
        self.radius = radius

    def get_bb(self):
        return self.pos[None, :] + np.array([-1, 1])[:, None] * self.radius

    def serialize(self):
        return np.concatenate((self.pos, [self.radius]))
