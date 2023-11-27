from typing import Union, Sequence

import numpy as np

from models.mesh import Mesh
from models.multi_mesh import merge_meshes
from models.primitives.circle import Circle
from transformations import get_rotation_matrix_x, get_translation_matrix, get_scale_matrix


class Cylinder(Mesh):
    def __init__(self,
                 radius: float = 1,
                 height: float = 1,
                 segments: int = 30,
                 smooth=True):
        base = Circle(radius=radius, vert_count=segments, center_point=True)
        base.transform_mesh(get_rotation_matrix_x(np.pi/2))
        top = base.copy()
        top.transform_mesh(get_translation_matrix(dy=height))
        top.flip_normals()
        side_vertices = np.vstack([base.vertices[1:, :], top.vertices[1:, :]])
        side_triangle_indices = np.zeros((segments * 2, 3))
        side_triangle_indices[:segments, 0] = np.arange(segments)
        side_triangle_indices[:segments, 1] = np.arange(segments) + 1
        side_triangle_indices[segments-1, 1] = 0
        side_triangle_indices[:segments, 2] = np.arange(segments) + segments

        side_triangle_indices[segments:, 0] = np.arange(segments) + segments + 1
        side_triangle_indices[segments:, 1] = np.arange(segments) + segments
        side_triangle_indices[-1, 0] = segments
        side_triangle_indices[segments:, 2] = np.arange(segments) + 1
        side_triangle_indices[-1, 2] = 0

        side_walls = Mesh(vertices=side_vertices, triangle_indices=side_triangle_indices.astype(int))
        side_walls.flip_normals()
        if not smooth:
            side_walls.flatten()
        vertices, indices, _, normals = merge_meshes([base, top, side_walls])
        super().__init__(vertices, indices, normals=normals)
        if not smooth:
            self.flatten()
