import time

import numpy as np

from models.circle import Circle
from models.multi_mesh import MultiMesh
from models.particle_system import ParticleSystem
from models.sphere import Sphere
from simulations.pendulum import Pendulum
from visualisation.renderable_factory import get_renderable
from visualisation.visobject import VisObject
from visualisation.meshViewer import MeshViewWindow
from visualisation.wireframe import Wireframe


if __name__ == "__main__":
    length = 2
    count = 1000
    pos = np.zeros((count, 3))
    # pos[:, 0] = np.linspace(0, 1, count) * length * np.sin(np.linspace(0, 2 * np.pi, count))
    # pos[:, 2] = np.linspace(0, 1, count) * length * np.cos(np.linspace(0, 2 * np.pi, count))
    pos[:, 0] = np.linspace(0, 1, count) * length
    # pos[:, 1] = np.arange(count) % 2
    p = Pendulum(particles=pos, substeps=100, mesh_scale=0.01)
    p.static[0] = 1
    p.update_compliances()
    # TODO: remove get_renderable method, add meshes of particle system separately
    particles_vis = VisObject(p.particles_mesh)
    links_vis = Wireframe(p.links_mesh)
    particles_vis.material.diffuse = np.ones(3)
    # particles_vis.shader_name = 'lines'
    win = MeshViewWindow(add_floorgrid=True, orthographic=True)
    win.add_object(particles_vis)
    win.add_object(links_vis)
    win.start()
    for i in range(1000):
        p.simulate(1/60, [0, -10, 0])
        #
        time.sleep(1/60)
        # p.update_meshes()
    pass