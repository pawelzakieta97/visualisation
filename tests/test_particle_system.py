import numpy as np

from models.circle import Circle
from models.multi_mesh import MultiMesh
from models.particle_system import ParticleSystem
from models.sphere import Sphere
from visualisation.visobject import VisObject
from visualisation.meshViewer import MeshViewWindow


if __name__ == "__main__":
    ps = ParticleSystem()
    c = Circle(radius=1)
    win = MeshViewWindow().init_default()
    for i in range(5):
        win.add_object(ps)
    win.run()
