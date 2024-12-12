import numpy as np
from OpenGL.GL import *  # pylint: disable=W0614

from models.wireframe import Wireframe
from visualisation.shader import Shader


class FloorGrid(Wireframe):

    def __init__(self, line_count: int = 21, line_spacing: float = 1):
        line_min = (line_count - 1)/2 * line_spacing
        line_max = -(line_count - 1)/2 * line_spacing
        ls = np.linspace(line_min, line_max, line_count)
        lines_x = np.zeros((line_count, 2, 3))
        lines_x[:, 0, 0] = line_min
        lines_x[:, 1, 0] = line_max
        lines_x[:, :, 2] = ls[:, None]

        lines_y = np.zeros((line_count, 2, 3))
        lines_y[:, 0, 2] = line_min
        lines_y[:, 1, 2] = line_max
        lines_y[:, :, 0] = ls[:, None]

        lines = np.vstack((lines_x, lines_y)).reshape(-1, 3)
        colors = np.ones_like(lines) * 0.2
        colors[line_count-1: line_count+1, 0] = 1
        colors[3*line_count-1: 3*line_count+1, 2] = 1
        super().__init__(lines=lines, colors=colors)
