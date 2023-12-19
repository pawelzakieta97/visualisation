import numpy as np
from OpenGL.GL import *  # pylint: disable=W0614

from transformations import get_orthographic_projection_matrix, look_at, get_perspective_projection_matrix
from visualisation.shader import Shader


class Light:
    def __init__(self, position: np.array = None, color: np.array = None, cast_shadows: bool = False, res=1024):
        if position is None:
            position = np.array([10, 10, 10])
        if color is None:
            color = np.array([1, 1, 1])
        self.position = position
        self.color = color
        self.cast_shadows = cast_shadows
        self.depth_map = None
        self.res = res
        self.shadow_map_size = 10
        self.near = 0.1
        self.far = 1000

    def get_transformation_matrix(self):

        projection_matrix = get_perspective_projection_matrix(fov=np.pi * 0.8, aspect_ratio=1,
                                                              near=self.near, far=self.far)
        view_matrix = look_at(self.position, target=np.zeros(3))
        return projection_matrix @ np.linalg.inv(view_matrix)

    def load(self):
        self.depth_map = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.depth_map)
        # THIS LINE BREAKS DEBUGGING????
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, self.res, self.res, 0, GL_DEPTH_COMPONENT,
                     GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glBindTexture(GL_TEXTURE_2D, 0)
