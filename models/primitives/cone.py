import numpy as np

from models.mesh import Mesh
from models.multi_mesh import merge_meshes
from models.primitives.circle import Circle
from transformations import get_rotation_matrix_x


class Cone(Mesh):
    def __init__(self, segments: int = 16, height: float = 1, center_point=False, single_top=False):
        base = Circle(vert_count=segments, center_point=False)
        base.transform_mesh(get_rotation_matrix_x(np.pi/2))
        side_triangles = np.zeros((segments, 3)).astype(int)
        top = np.array([[0, height, 0]])
        if not single_top:
            top = np.vstack([top]*segments)
        cycled_base_indices = np.arange(segments).tolist() + [0]
        side_triangles[:, 1:] = np.lib.stride_tricks.sliding_window_view(cycled_base_indices, 2)
        if single_top:
            side_triangles[:, 0] = segments
        else:
            side_triangles[:, 0] = np.arange(segments) + segments
        side_vertices = np.vstack((base.vertices, top))
        base = Circle(vert_count=segments, center_point=center_point)
        base.transform_mesh(get_rotation_matrix_x(np.pi/2))

        merged_verts, merged_triangle_indices, merged_colors, merged_normals = (
            merge_meshes([base, Mesh(vertices=side_vertices, triangle_indices=side_triangles)]))
        super().__init__(merged_verts, merged_triangle_indices, normals=merged_normals)
