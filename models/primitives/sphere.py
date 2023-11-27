import numpy as np

from models.mesh import Mesh
from models.primitives.cube import get_unit_cube_vertices


class Sphere(Mesh):
    def __init__(self, radius: float = 1.0, smoothness=1,
                 smooth=True):
        vertices, triangle_indices = get_unit_cube_vertices()
        vertices -= 0.5
        super().__init__(vertices, triangle_indices)
        for i in range(smoothness):
            self.subdivide2()

        vert_distances = np.linalg.norm(self.vertices, axis=1)
        self.vertices *= radius / vert_distances[:, None]
        if not smooth:
            self.flatten()
        self.normals = self.get_normals()

