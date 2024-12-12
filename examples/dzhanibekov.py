import numpy as np
from sympy import Plane

from models.coords import Arrow
from models.mesh import Mesh
from models.multi_mesh import merge_meshes
from models.primitives.cube import Cube
from models.wireframe import Wireframe
from simulations.collider import Collider
from simulations.collision_detector import CollisionDetector, get_collisions
from simulations.xpbd import XPBD
from visualisation.meshViewer import MeshViewWindow

if __name__ == '__main__':
    cube_mesh = Cube()
    cube_mesh.vertices *= np.array([7, 1, 1])
    cube_mesh1 = Cube()
    cube_mesh1.vertices += np.array([3, 1, 0])
    cube_mesh = merge_meshes([cube_mesh, cube_mesh1], as_mesh=True)
    cube = Collider(cube_mesh)
    # cube.mesh.translate(dy=3)
    # cube.mesh.rotate_y(np.pi/4)
    # cube.mesh.rotate_x(np.pi/3)
    cube.w = np.array([0.1,1,0]) * 10.0


    win = MeshViewWindow(add_floorgrid=True, orthographic=False, target_fps=60)
    win.add_object(cube.mesh)
    win.add_object(cube.mesh)

    arrow = Arrow()
    xpbd = XPBD([cube])
    win.add_object(arrow)
    # xpbd.step()
    arrow.set(start=cube.mesh.transformation[:3, 3],
              end=cube.mesh.transformation[:3, 3] + cube.mesh.transformation[:3, :3] @ cube.w)

    def tick():
        # xpbd.step()
        arrow.set(start=cube.mesh.transformation[:3, 3],
                  end=cube.mesh.transformation[:3, 3] + cube.mesh.transformation[:3, :3] @ cube.w)

    win.run(tick)


