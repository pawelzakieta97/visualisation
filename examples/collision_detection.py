import numpy as np
from sympy import Plane

from models.mesh import Mesh
from models.primitives.cube import Cube
from models.wireframe import Wireframe
from simulations.collider import Collider
from simulations.collision_detector import CollisionDetector, get_collisions
from visualisation.meshViewer import MeshViewWindow

if __name__ == '__main__':
    c1 = Collider(Cube())
    c2 = Collider(Cube())
    plane = Mesh(vertices=np.array([[-1, 0, -1],
                                    [-1, 0, 1],
                                    [1, 0, 1],
                                    [1, 0, -1]]) * 10.0,
                 triangle_indices=np.array([[0, 1, 2], [2, 3, 0]]))
    c3 = Collider(plane)
    c2.mesh.translate(dx=-1.1, dz=0.1, dy=-0.1)
    c2.mesh.rotate_y(np.pi/4)
    c2.mesh.rotate_z(np.pi/4)
    p1, p2, l = get_collisions(c3, c2)
    collision_line1 = np.stack((p1,p2))
    collision1 = Wireframe(collision_line1, np.ones_like(collision_line1))

    p1, p2, l = get_collisions(c1, c2)
    collision_line2= np.stack((p1,p2))
    collision2 = Wireframe(collision_line2, np.ones_like(collision_line2))
    win = MeshViewWindow(add_floorgrid=True, orthographic=False, target_fps=60)
    win.add_object(c1.mesh)
    win.add_object(c2.mesh)
    win.add_object(collision1)
    win.add_object(collision2)
    win.run()

