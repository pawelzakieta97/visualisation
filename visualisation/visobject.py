from enum import Enum
from typing import Type

import numpy as np
from OpenGL.GL import *  # pylint: disable=W0614

from transformations import get_translation_matrix
from visualisation.light import Light
from visualisation.material import Material, Texture
from visualisation.renderable import Renderable
from visualisation.shader import Shader


from models.mesh import Mesh


class ColorMode(Enum):
    UNIFORM = 0
    VERTEX_COLOR = 1
    UV = 2


class VisObject(Renderable):

    def __init__(self, mesh: Mesh, material: Material = None, casts_shadows=True, shader_cls: Type[Shader] = None):
        if material is None:
            material = Material()
        super().__init__(material=material, shader_cls=shader_cls)
        self.indices_buffer = None
        self.normal_buffer = None
        self.vertex_buffer = None
        self.uv_buffer = None
        self.color_buffer = None
        self.mesh = mesh
        self.material = material
        self.casts_shadows = casts_shadows

    def get_color_mode(self):
        if any([isinstance(feature, Texture) for
                feature in [self.material.diffuse, self.material.glossiness, self.material.reflectiveness]]):
            return ColorMode.UV
        elif np.ndim(self.mesh.color) == 2:
            return ColorMode.VERTEX_COLOR
        else:
            return ColorMode.UNIFORM

    def load_vbos(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
        glBufferData(GL_ARRAY_BUFFER, self.mesh.vertices.astype(np.float32), GL_STATIC_DRAW)

        if self.get_color_mode() == ColorMode.UNIFORM:
            self.color_buffer = None
        elif self.get_color_mode() == ColorMode.VERTEX_COLOR:
            # TODO: drop per-vertex color support?
            glBindBuffer(GL_ARRAY_BUFFER, self.color_buffer)
            glBufferData(GL_ARRAY_BUFFER, self.mesh.color.astype(np.float32), GL_STATIC_DRAW)
        elif self.get_color_mode() == ColorMode.UV:
            glBindBuffer(GL_ARRAY_BUFFER, self.uv_buffer)
            glBufferData(GL_ARRAY_BUFFER, self.mesh.uv.astype(np.float32), GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, self.normal_buffer)
        glBufferData(GL_ARRAY_BUFFER, self.mesh.normals.astype(np.float32), GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.indices_buffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.mesh.triangle_indices.astype(np.uint32), GL_STATIC_DRAW)

    def load(self):
        # glBindVertexArray(self.vertex_array_object)

        self.vertex_buffer = glGenBuffers(1)
        self.normal_buffer = glGenBuffers(1)
        self.indices_buffer = glGenBuffers(1)
        self.color_buffer = glGenBuffers(1)
        self.uv_buffer = glGenBuffers(1)
        # self.load_shader()
        # self.load_vbos()
        self.material.load()
