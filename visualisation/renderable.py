import os
from typing import Sequence

from visualisation.material import Material
from visualisation.shader import Shader


class Renderable(object):
    SHADER_DIRECTORY = os.path.join(os.path.dirname(__file__), 'glsl')

    def __init__(self, material: Material = None):
        self.shader = None
        self.material = material

    def makeContext(self):
        self.load_shader()
        self.load_object()
        # self.loadTexture()
        return self

    def load_shader(self):
        self.shader = Shader()

    def load_object(self):
        print("Make and fill OPENGL buffers,vertex,uv,normal,trangent,indices")

    def render(self, projection_matrix, view_matrix, camera_position, light):
        print("override rendering process")
        pass


class CompoundRenderable(Renderable):
    def __init__(self, objects: Sequence[Renderable]):
        super().__init__()
        self.objects = objects

    def render(self, projection_matrix, view_matrix, camera_position, light):
        for obj in self.objects:
            obj.render(projection_matrix, view_matrix, camera_position, light)

    def load_shader(self):
        for obj in self.objects:
            obj.load_shader()

    def load_object(self):
        for obj in self.objects:
            obj.load_object()

    def makeContext(self):
        for obj in self.objects:
            obj.makeContext()
        return self
