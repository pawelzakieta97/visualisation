import numpy as np

from models.mesh import Mesh
from models.parse_obj import parse_obj
from transformations import get_scale_matrix
from visualisation.meshViewer import MeshViewWindow

if __name__ == "__main__":
    vertices, triangles = parse_obj('../obj/bunny.obj')
    bunny = Mesh(vertices=vertices, triangle_indices=triangles)
    bunny.transform_mesh(get_scale_matrix(20, 20, 20))
    win = MeshViewWindow(add_floorgrid=True, orthographic=False, target_fps=600)
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
    plane = win.add_object(plane)
    win.add_object(bunny)
    win.run()
