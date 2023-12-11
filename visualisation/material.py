import numpy as np
from OpenGL.GL import *  # pylint: disable=W0614


class Material:
    def __init__(self, diffuse=None, reflectiveness=None, glossiness=0.5):
        if diffuse is None:
            diffuse = np.array([0.5, 0.5, 0.5])
        if reflectiveness is None:
            reflectiveness = np.array([1, 1, 1])
        self.reflectiveness = reflectiveness
        self.glossiness = glossiness
        if np.ndim(diffuse) > 1:
            diffuse = Texture(diffuse)
        self.diffuse = diffuse

    def load(self):
        for v in [self.reflectiveness, self.glossiness, self.diffuse]:
            if isinstance(v, Texture):
                v.load()


class Texture:
    def __init__(self, data: np.array):
        self.texture_id = glGenTextures(1)
        self.data = data

    def load(self):
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        imgData = self.data.astype(np.uint8)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.data.shape[1], self.data.shape[0],
                     0, GL_RGB, GL_UNSIGNED_BYTE, imgData)
