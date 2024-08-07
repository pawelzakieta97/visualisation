import numpy as np

from models.mesh import Mesh
from models.parse_obj import parse_obj
from transformations import get_scale_matrix, get_translation_matrix
from visualisation.meshViewer import MeshViewWindow

if __name__ == "__main__":
    vertices, triangles = parse_obj('../obj/bunny_normalized.obj')
    bunny = Mesh(vertices=vertices, triangle_indices=triangles)
    win = MeshViewWindow(add_floorgrid=True, orthographic=False, target_fps=60)
    win.controller.pos = np.array([0, 2, 5.0])
    win.controller.yaw = 0
    win.controller.pitch = 0
    win.controller.fov=90
    win.light.cast_shadows = True
    plane = Mesh(vertices=np.array([[-1, 0, -1],
                                    [-1, 0, 1],
                                    [1, 0, 1],
                                    [1, 0, -1]]) * 10,
                 triangle_indices=np.array([[0, 1, 2], [2, 3, 0]]),
                 uv=np.array([[0, 0],
                              [1, 0],
                              [1, 1],
                              [0, 1]]))
    # plane = win.add_object(plane)
    win.add_object(bunny)
    win.run()
