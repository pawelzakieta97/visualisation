import numpy as np

from models.circle import Circle
from models.multi_mesh import MultiMesh
from models.particle_system import ParticleSystem
from models.sphere import Sphere
from visualisation.renderable_factory import get_renderable
from visualisation.visobject import VisObject
from visualisation.meshViewer import MeshViewWindow


if __name__ == "__main__":
    ps = ParticleSystem(particle_count=100)#, reference_mesh=Circle(radius=0.03))
    ps.add_links(np.random.randint(0, 99, size=(100, 2)))
    ps.update_meshes()
    # TODO: remove get_renderable method, add meshes of particle system separately
    ps_vis = get_renderable(ps)
    ps_vis.objects[0].material.diffuse = np.ones(3)
    ps_vis.objects[0].shader_name = 'lines'
    win = MeshViewWindow(add_floorgrid=True)
    win.add_object(ps_vis)
    win.run()
