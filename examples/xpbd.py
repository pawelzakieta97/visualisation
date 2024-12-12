import numpy as np
from sympy import Plane

from models.coords import Arrow
from models.mesh import Mesh
from models.primitives.cube import Cube
from models.wireframe import Wireframe
from simulations.collider import Collider
from simulations.collision_detector import CollisionDetector, get_collisions
from simulations.xpbd import XPBD
from visualisation.meshViewer import MeshViewWindow

if __name__ == '__main__':
    cube_mesh = Cube()
    cube_mesh.vertices *= np.array([1,2, 0.2])
    cube = Collider(cube_mesh)
    plane = Mesh(vertices=np.array([[-1, 0, -1],
                                    [-1, 0, 1],
                                    [1, 0, 1],
                                    [1, 0, -1]]) * 10.0,
                 triangle_indices=np.array([[0, 1, 2], [2, 3, 0]]))
    plane = Collider(plane, static=True)
    cube.mesh.translate(dy=3)
    # cube.mesh.rotate_y(np.pi/4)
    # cube.mesh.rotate_z(np.pi/4)
    # cube.mesh.rotate_x(np.pi/3)
    cube.w = np.array([1,0.2,0]) * 3.0


    arrow = Arrow()
    win = MeshViewWindow(add_floorgrid=True, orthographic=False, target_fps=60)
    win.add_object(cube.mesh)
    win.add_object(plane.mesh)
    win.add_object(arrow)
    xpbd = XPBD([cube])
    def tick():
        xpbd.step()
        arrow.set(start=cube.mesh.transformation[:3, 3],
                  end=cube.mesh.transformation[:3, 3] + cube.mesh.transformation[:3, :3] @ cube.w)

    win.run(tick)

