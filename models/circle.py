import numpy as np

from models.mesh import Mesh
from models.cube import get_unit_cube_vertices


class Sphere(Mesh):
    def __init__(self, radius: float = 1.0, vert_count=30):
        angles = np.arange(0, np.pi * 2, vert_count, endpoints=False)
        x = np.cos(angles) * radius
        y = np.sin(angles) * radius
        vertices = np.zeros((vert_count, 3))
        vertices[:, 0] = x
        vertices[:, 1] = y
        normals = np.zeros((vert_count, 3))
        normals[:, 2] = 1
        triangle_indices = np.zeros((vert_count, 3))


