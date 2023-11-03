from models.compound_mesh import CompoundMesh
from models.mesh import Mesh
from visualisation.renderable import Renderable, CompoundRenderable
from visualisation.visobject import VisObject
from visualisation.wireframe import Wireframe
from models.wireframe import Wireframe as WireframeModel


def get_renderable(model) -> Renderable:
    if isinstance(model, Mesh):
        return VisObject(model)
    if isinstance(model, WireframeModel):
        return Wireframe(model)
    if isinstance(model, CompoundMesh):
        return CompoundRenderable([get_renderable(m) for m in model.get_meshes()])
    raise ValueError(f'model type {type(model)} not supported')
