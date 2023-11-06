import numpy as np

from models.circle import Circle
from models.multi_mesh import MultiMesh
from models.particle_system import ParticleSystem
from models.sphere import Sphere
from visualisation.renderable_factory import get_renderable
from visualisation.visobject import VisObject
from visualisation.meshViewer import MeshViewWindow


if __name__ == "__main__":
    ps = ParticleSystem(particle_count=100, reference_mesh=Circle(radius=0.03))
    ps_vis = get_renderable(ps)
    ps_vis.objects[0].material.diffuse = np.ones(3)
    ps_vis.objects[0].shader_name = 'lines'
    win = MeshViewWindow(add_floorgrid=True)
    for i in range(5):
        win.add_object(ps_vis)
    win.run()
