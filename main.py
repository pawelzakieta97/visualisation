import numpy as np

from models.circle import Circle
from models.multi_mesh import MultiMesh
from models.sphere import Sphere
from visualisation.visobject import VisObject
from visualisation.meshViewer import MeshViewWindow


if __name__ == "__main__":
    sphere = Sphere(radius=0.05, vert_count=14)
    c = Circle(radius=1)
    win = MeshViewWindow(add_floorgrid=True)
    for i in range(5):
        # sphere = Sphere(radius=0.1, vert_count=500)
        spheres = MultiMesh(sphere, count=4000)
        positions = np.random.random((4000, 3)) * 15 - 8
        spheres.set_positions(positions)
        win.add_object(VisObject(c, mode_2d=False))
    # win.run()
    import threading
    import time
    win.start()
    print('code continues')
    # win.run()
