import numpy as np

from models.mesh import Mesh


class Circle(Mesh):
    def __init__(self, radius: float = 1.0, vert_count=30, center_point=True):
        angles = np.linspace(0, np.pi * 2, vert_count, endpoint=False)
        x = np.cos(angles) * radius
        y = np.sin(angles) * radius
        if vert_count < 5:
            center_point = False
        if center_point:
            vertices = np.zeros((vert_count + 1, 3))
            vertices[1:, 0] = x
            vertices[1:, 1] = y
            normals = np.zeros((vert_count + 1, 3))
            normals[:, 2] = 1
            triangle_indices = np.zeros((vert_count, 3)).astype(int)
            triangle_indices[:, 1] = np.arange(vert_count) + 1
            triangle_indices[:-1, 2] = np.arange(1, vert_count) + 1
            triangle_indices[-1, 2] = 1
        else:
            vertices = np.zeros((vert_count, 3))
            vertices[:, 0] = x
            vertices[:, 1] = y
            triangle_indices = np.zeros((vert_count-2, 3)).astype(int)
            triangle_indices[:, 1:] = np.lib.stride_tricks.sliding_window_view(np.arange(1,vert_count), 2)

        normals = np.zeros_like(vertices)
        normals[:, 2] = 1
        super().__init__(vertices, triangle_indices, normals=normals)


if __name__ == '__main__':
    s = Circle(vert_count=4)
