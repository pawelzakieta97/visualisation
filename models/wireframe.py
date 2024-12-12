import numpy as np

from transformations import get_translation_matrix


class Wireframe:
    def __init__(self, lines: np.array, colors: np.array):
        super().__init__()
        self.transformation = np.eye(4)
        self.lines = lines
        self.colors = colors
        self.changed = True

    def transform(self, transform_matrix):
        self.transformation = self.transformation @ transform_matrix

    def translate(self, *args, **kwargs):
        self.transform(get_translation_matrix(*args, **kwargs))