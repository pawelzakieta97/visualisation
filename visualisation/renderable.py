import os
from typing import Sequence

from visualisation.material import Material
from visualisation.shader import Shader


class Renderable(object):
    SHADER_DIRECTORY = os.path.join(os.path.dirname(__file__), 'glsl')

    def __init__(self, material: Material = None):
        self.shader = None
        self.material = material
        self.shader = Shader()

    def load(self):
        pass

    def render(self, mvp, camera_position, light):
        print("override rendering process")
        pass


class CompoundRenderable(Renderable):
    def __init__(self, objects: Sequence[Renderable]):
        super().__init__()
        self.objects = objects

    def render(self, mvp, camera_position, light):
        for obj in self.objects:
            obj.render(mvp, camera_position, light)

    def load(self):
        for obj in self.objects:
            obj.load()
