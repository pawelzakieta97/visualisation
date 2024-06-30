import numpy as np

from raytracing.renderable import Renderable
from models.primitives.sphere import Sphere as SphereMesh


class Triangle(Renderable):
    def __init__(self, data: np.array):
        self.data = data
        a = data[1, :] - data[:, 0]
        b = data[2, :] - data[:, 1]
        normal = np.cross(a, b)
        self.normal = normal / np.linalg.norm(normal)

    def get_bb(self):
        return np.stack((self.data.min(axis=0), self.data.max(axis=0)))

    def serialize(self):
        return np.concatenate((self.data.flatten(), self.normal))
