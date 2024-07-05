import numpy as np

from raytracing.renderable import Renderable
from models.primitives.sphere import Sphere as SphereMesh


class Triangle(Renderable):
    def __init__(self, data: np.array):
        self.data = data
        a = data[1, :] - data[0, :]
        b = data[2, :] - data[1, :]
        normal = np.cross(a, b)
        self.normal = normal / np.linalg.norm(normal)
        T = data.T
        T = np.concatenate((T, np.ones((1, 3))))
        self. T = np.linalg.inv(T.T @ T) @ T.T
        self.h = np.dot(normal, data[0, :])

    def get_bb(self):
        return np.stack((self.data.min(axis=0), self.data.max(axis=0)))

    def serialize(self):
        return np.concatenate((self.T.flatten(), self.normal, [self.h]))
