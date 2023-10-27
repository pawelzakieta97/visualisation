import numpy as np


class Material:
    def __init__(self, diffuse=None, reflectiveness=None, glossiness=0.5):
        if diffuse is None:
            diffuse = np.array([0.5, 0.5, 0.5])
        if reflectiveness is None:
            reflectiveness = np.array([1, 1, 1])
        self.diffuse = diffuse
        self.reflectiveness = reflectiveness
        self.glossiness = glossiness
