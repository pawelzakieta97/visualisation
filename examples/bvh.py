import pickle

from PIL import Image

import numpy as np

from models.mesh import Mesh
from models.primitives.cube import Cube
from models.primitives.sphere import Sphere as SphereMesh
from models.wireframe import Wireframe
from raytracing.bvh import get_object_tree_greedy
from raytracing.sphere import Sphere
from visualisation.meshViewer import MeshViewWindow

np.random.seed(2)
if __name__ == "__main__":
    win = MeshViewWindow(add_floorgrid=True, orthographic=False, target_fps=60)
    win.light.position[2] = 7
    tree = pickle.load(open('bvh.p', 'rb'))
    for triangle in tree.get_elements():
        triangle_mesh = Mesh(triangle.data, np.array([[0,1,2],[1,2,0],[2,1,0]]))
        win.add_object(triangle_mesh)
    bbs = tree.get_bbs()

    # bbs = [[np.array([[0,0,0],[1,1,1]])]]
    level = 0
    for level_bbs in bbs:
        for bb in level_bbs:
            lines = [[bb[0, 0], bb[0, 1], bb[0, 2]],
                     [bb[1, 0], bb[0, 1], bb[0, 2]],

                     [bb[1, 0], bb[0, 1], bb[0, 2]],
                     [bb[1, 0], bb[1, 1], bb[0, 2]],

                     [bb[1, 0], bb[1, 1], bb[0, 2]],
                     [bb[0, 0], bb[1, 1], bb[0, 2]],

                     [bb[0, 0], bb[1, 1], bb[0, 2]],
                     [bb[0, 0], bb[0, 1], bb[0, 2]],

                     [bb[0, 0], bb[0, 1], bb[1, 2]],
                     [bb[1, 0], bb[0, 1], bb[1, 2]],

                     [bb[1, 0], bb[0, 1], bb[1, 2]],
                     [bb[1, 0], bb[1, 1], bb[1, 2]],

                     [bb[1, 0], bb[1, 1], bb[1, 2]],
                     [bb[0, 0], bb[1, 1], bb[1, 2]],

                     [bb[0, 0], bb[1, 1], bb[1, 2]],
                     [bb[0, 0], bb[0, 1], bb[1, 2]],

                     [bb[0, 0], bb[0, 1], bb[0, 2]],
                     [bb[0, 0], bb[0, 1], bb[1, 2]],

                     [bb[1, 0], bb[0, 1], bb[0, 2]],
                     [bb[1, 0], bb[0, 1], bb[1, 2]],

                     [bb[1, 0], bb[1, 1], bb[0, 2]],
                     [bb[1, 0], bb[1, 1], bb[1, 2]],

                     [bb[0, 0], bb[1, 1], bb[0, 2]],
                     [bb[0, 0], bb[1, 1], bb[1, 2]],
                     ]
            lines = np.array(lines)
            color = np.array([1, 1-level / (len(bbs)-1), 1-level / (len(bbs)-1)])
            colors = np.ones_like(lines)
            colors[:, :] = color
            wireframe = Wireframe(lines, colors=colors)
            win.add_object(wireframe)
        level += 1
    win.controller.pos = np.array([-0.5,1,3.0])
    win.controller.yaw = 0
    win.controller.pitch = 0
    win.controller.fov=90
    win.run()

