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
    pos = np.array([[0, 0, 0],
                    [1, -1, 0],
                    [0, -2, 0],
                    [1, -3, 0]])
    p = Pendulum(particles=pos)
    # TODO: remove get_renderable method, add meshes of particle system separately
    particles_vis = VisObject(p.particles_mesh)
    links_vis = Wireframe(p.links_mesh)
    particles_vis.material.diffuse = np.ones(3)
    particles_vis.shader_name = 'lines'
    win = MeshViewWindow(add_floorgrid=True)
    win.add_object(particles_vis)
    win.add_object(links_vis)
    win.start()
    for i in range(100):
        p.simulate(1/60, [0, -10, 0])

        time.sleep(1/60)
    # p.simulate(1 / 60, [0, -10, 0])
    pass