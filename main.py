import numpy as np

from models.primitives.circle import Circle
from models.multi_mesh import MultiMesh
from models.primitives.sphere import Sphere
from models.primitives.cube import Cube
from visualisation.visobject import VisObject
from visualisation.meshViewer import MeshViewWindow
from transformations import get_translation_matrix


if __name__ == "__main__":
    sphere = Sphere(radius=0.05, vert_count=14)
    spheres = MultiMesh(sphere, count=400)
    positions = np.random.random((400, 3)) * 15 - 8
    spheres.set_positions(positions)
    cube = Cube()
    cube.transformation = get_translation_matrix(dx=-2)
    circle = Circle(radius=1)
    circle.transformation = get_translation_matrix(dx=2)
    sphere = Sphere(radius=1, vert_count=50)
    win = MeshViewWindow(add_floorgrid=True, orthographic=False)
    win.add_object(VisObject(circle))
    win.add_object(VisObject(cube))
    win.add_object(VisObject(sphere))
    win.add_object(VisObject(spheres))
    win.start()
    print('code continues')
    # win.run()
