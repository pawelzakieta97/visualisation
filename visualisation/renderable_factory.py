from typing import Union, Type

from models.compound_mesh import CompoundMesh
from models.mesh import Mesh
from visualisation.map import Map
from visualisation.renderable import CompoundRenderable
from visualisation.shader import Shader
from visualisation.shaders.line_shader import LineShader
from visualisation.shaders.stadard_shader import StandardShader
from visualisation.visobject import VisObject
from visualisation.wireframe import Wireframe
from models.wireframe import Wireframe as WireframeModel


def get_renderable(model, shader_cls: Type[Shader], *args, **kwargs) -> Union[VisObject, Wireframe, CompoundRenderable]:
    if isinstance(model, Mesh):
        return VisObject(model, shader_cls=shader_cls, *args, **kwargs)
    if isinstance(model, WireframeModel):
        return Wireframe(model, *args, **kwargs)
    if isinstance(model, CompoundMesh):
        return CompoundRenderable([get_renderable(m, *args, **kwargs) for m in model.get_meshes()])
    raise ValueError(f'model type {type(model)} not supported')


DEFAULT_OBJECT_SHADERS = {
    VisObject: StandardShader,
    Wireframe: LineShader,
    Map: StandardShader
}