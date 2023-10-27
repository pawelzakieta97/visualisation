import numpy as np

from models.mesh import Mesh
from models.cube import get_unit_cube_vertices


class Sphere(Mesh):
    def __init__(self, radius: float = 1.0, vert_count=30,
                 smooth=True):
        vertices, triangle_indices = get_unit_cube_vertices()
        vertices -= 0.5
        super().__init__(vertices, triangle_indices)
        while self.vertices.shape[0] < vert_count:
            max_edge = np.argmax(self.get_edge_lengths())
            # max_edge = 0
            self.subdivide(max_edge)

        vert_distances = np.linalg.norm(self.vertices, axis=1)
        self.vertices *= radius / vert_distances[:, None]
        if not smooth:
            self.flatten()
        self.normals = self.get_normals()

