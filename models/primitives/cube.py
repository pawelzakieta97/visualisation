from typing import Union, Sequence

import numpy as np

from models.mesh import Mesh


def get_unit_cube_vertices(uv=False):
    vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1],
                       [0, 1, 0], [1, 1, 0], [1, 1, 1], [0, 1, 1]]).astype(float)
    bottom_triangles = np.array([[0, 1, 2], [2, 3, 0]])
    # 6, 5, 4, 7
    top_triangles = np.array([[6, 5, 4], [4, 7, 6]])
    # 4, 5, 1, 0
    front_triangles = np.array([[4, 5, 1], [1, 0, 4]])
    # 6, 7, 3, 2
    back_triangles = np.array([[6, 7, 3], [3, 2, 6]])
    # 0, 3, 7, 4
    left_triangles = np.array([[0, 3, 7], [7, 4, 0]])
    # 2, 1, 5, 6
    right_triangles = np.array([[2, 1, 5], [5, 6, 2]])
    triangle_indices = np.concatenate((bottom_triangles,
                                       top_triangles,
                                       front_triangles,
                                       back_triangles,
                                       left_triangles,
                                       right_triangles))
    return vertices, triangle_indices


class Cube(Mesh):
    def __init__(self, position: Sequence = None,
                 size: Union[float, Sequence] = 1.0,
                 smooth=False):
        vertices, triangle_indices = get_unit_cube_vertices()
        if position is None:
            position = [0, 0, 0]
        if isinstance(size, float) or isinstance(size, int):
            size = [size, size, size]
        vertices *= np.array(size)[None, :]
        vertices += np.array(position)[None, :]
        super().__init__(vertices, triangle_indices)
        if not smooth:
            self.flatten()
            self.uv = np.zeros((self.vertices.shape[0], 2))
            self.uv = self.get_uv()

    def get_uv(self):
        uvs = np.zeros((self.vertices.shape[0], 2))

        top_triangles = self.normals[:, 1] > 0.99
        bottom_triangles = self.normals[:, 1] < -0.99
        horizontal_triangles = np.logical_or(top_triangles, bottom_triangles)
        origin = self.vertices[horizontal_triangles, :].min(axis=0)
        uvs[horizontal_triangles, :] = (self.vertices[horizontal_triangles, :] - origin)[:, [0,2]]

        right_triangles = self.normals[:, 0] > 0.99
        left_triangles = self.normals[:, 0] < -0.99
        side_triangles = np.logical_or(right_triangles, left_triangles)
        origin = self.vertices[side_triangles, :].min(axis=0)
        uvs[side_triangles, :] = (self.vertices[side_triangles, :] - origin)[:, 1:]

        front_triangles = self.normals[:, 2] > 0.99
        back_triangles = self.normals[:, 2] < -0.99
        forward_triangles = np.logical_or(front_triangles, back_triangles)
        origin = self.vertices[forward_triangles, :].min(axis=0)
        uvs[forward_triangles, :] = (self.vertices[forward_triangles, :] - origin)[:, :2]
        return uvs
        pass