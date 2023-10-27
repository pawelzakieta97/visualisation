import numpy as np


class Light:
    def __init__(self, position: np.array = None, color: np.array = None):
        if position is None:
            position = np.array([10, 10, 10])
        if color is None:
            color = np.array([1, 1, 1])
        self.position = position
        self.color = color