import numpy as np
from OpenGL.GL import *  # pylint: disable=W0614


class Material:
    def __init__(self, diffuse=None, reflectiveness=None, glossiness=0.5):
        if diffuse is None:
            diffuse = np.array([0.5, 0.5, 0.5])
        if reflectiveness is None:
            reflectiveness = np.array([1, 1, 1])
        self.diffuse = diffuse
        self.is_texture = np.ndim(diffuse) > 1
        self.reflectiveness = reflectiveness
        self.glossiness = glossiness
        self.texture_id = None
        if self.is_texture:
            self.load_vbos()

    def load_vbos(self):
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        imgData = self.diffuse.astype(np.uint8)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.diffuse.shape[1], self.diffuse.shape[1],
                     0, GL_RGB, GL_UNSIGNED_BYTE, imgData)
