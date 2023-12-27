import os
from typing import Sequence, Type

from visualisation.material import Material
from visualisation.shader import Shader


class Renderable(object):
    SHADER_DIRECTORY = os.path.join(os.path.dirname(__file__), 'glsl')

    def __init__(self, shader_cls: Type[Shader] = None,
                 material: Material = None):
        self.shader = None
        self.material = material
        self.shader = Shader()
        self.shader_cls = shader_cls

    def load(self):
        pass

    def render(self, projection_view_matrix, camera_position, light):
        print("override rendering process")
        pass


class CompoundRenderable(Renderable):
    def __init__(self, objects: Sequence[Renderable]):
        super().__init__()
        self.objects = objects

    def render(self, projection_view_matrix, camera_position, light):
        for obj in self.objects:
            obj.render(projection_view_matrix, camera_position, light)

    def load(self):
        for obj in self.objects:
            obj.load()
