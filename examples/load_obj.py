from models.mesh import Mesh
from models.parse_obj import parse_obj
from transformations import get_scale_matrix
from visualisation.meshViewer import MeshViewWindow

if __name__ == "__main__":
    vertices, triangles = parse_obj('../obj/bunny.obj')
    bunny = Mesh(vertices=vertices, triangle_indices=triangles)
    bunny.transform_mesh(get_scale_matrix(10, 10, 10))
    win = MeshViewWindow(add_floorgrid=True, orthographic=True, target_fps=30)
    win.add_object(bunny)
    win.run()
