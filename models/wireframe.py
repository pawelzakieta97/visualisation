import numpy as np


class Wireframe:
    def __init__(self, lines: np.array, colors: np.array):
        super().__init__()
        self.lines = lines
        self.colors = colors
