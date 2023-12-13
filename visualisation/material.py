import numpy as np
from OpenGL.GL import *  # pylint: disable=W0614


class Material:
    def __init__(self, diffuse=None, reflectiveness=None, glossiness=0.5, texture_interpolation=None):
        if diffuse is None:
            diffuse = np.array([0.5, 0.5, 0.5])
        if reflectiveness is None:
            reflectiveness = np.array([1, 1, 1])
        if np.ndim(diffuse) > 1:
            diffuse = Texture(diffuse, texture_interpolation)
        if np.ndim(reflectiveness) > 1:
            reflectiveness = Texture(reflectiveness, texture_interpolation)
        if np.ndim(glossiness) > 1:
            glossiness = Texture(glossiness, texture_interpolation)
        self.reflectiveness = reflectiveness
        self.diffuse = diffuse
        self.glossiness = glossiness

    def load(self):
        for v in [self.reflectiveness, self.glossiness, self.diffuse]:
            if isinstance(v, Texture):
                v.load()


class Texture:
    def __init__(self, data: np.array, texture_interpolation=None):
        self.texture_id = glGenTextures(1)
        self.data = data
        if texture_interpolation is None:
            texture_interpolation = GL_LINEAR
        self.texture_interpolation = texture_interpolation

    def load(self):
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        imgData = self.data.astype(np.uint8)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, self.texture_interpolation)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, self.texture_interpolation)
        if np.ndim(self.data) == 3:
            # rgb
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.data.shape[1], self.data.shape[0],
                         0, GL_RGB, GL_UNSIGNED_BYTE, imgData)
        elif np.ndim(self.data) == 2:
            # grayscale
            glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, self.data.shape[1], self.data.shape[0],
                         0, GL_LUMINANCE, GL_UNSIGNED_BYTE, imgData)
