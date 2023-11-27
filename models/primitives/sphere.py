import numpy as np

from models.mesh import Mesh
from models.primitives.cone import Cone
from models.primitives.cube import get_unit_cube_vertices


class Sphere(Mesh):
    def __init__(self, radius: float = 1.0, smoothness=2,
                 smooth=True):
        r = 1/3**0.5
        h = (1 - r**2)**0.5
        tetrahedron = Cone(radius=r, height=h, segments=3, single_top=True, center_point=False, separate_base=False)
        vertices = tetrahedron.vertices - np.array([0, 0.3, 0])
        triangle_indices = tetrahedron.triangle_indices
        super().__init__(vertices, triangle_indices)
        for i in range(smoothness):
            self.subdivide2()

        vert_distances = np.linalg.norm(self.vertices, axis=1)
        self.vertices *= radius / vert_distances[:, None]
        if not smooth:
            self.flatten()
        self.normals = self.get_normals()
        pass

