import numpy as np

from simulations.pendulum import Pendulum
from visualisation.visobject import VisObject
from visualisation.meshViewer import MeshViewWindow
from visualisation.wireframe import Wireframe

if __name__ == "__main__":
    length = 10
    count = 100
    pos = np.zeros((count, 3))
    pos[:, 0] = np.linspace(0, 1, count) * length
    # pos[:, 1] = np.arange(count) % 2
    p = Pendulum(particles=pos, substeps=500, mesh_scale=0.1)
    p.static[0] = 1
    p.update_compliances()
    particles_vis = VisObject(p.particles_mesh)
    links_vis = Wireframe(p.links_mesh)
    particles_vis.material.diffuse = np.ones(3)
    fps = 60


    def tick():
        p.simulate_fast(1 / fps, [0, -10, 0])


    win = MeshViewWindow(add_floorgrid=True, orthographic=True,
                         tick_func=tick, target_fps=fps)
    win.add_object(particles_vis)
    win.add_object(links_vis)
    win.run()
