import numpy as np

from models.mesh import Mesh
from models.primitives.cone import Cone
from models.primitives.cube import get_unit_cube_vertices


def get_icosahedron():
    angles = np.linspace(0, np.pi * 2, 5, endpoint=False)
    n = 5
    total_angle = (n - 2) * np.pi
    angle = total_angle / n / 2
    R = 1 / np.cos(angle) / 2
    r = R * np.sin(angle)
    x1 = np.cos(angles) * R
    y1 = np.sin(angles) * R
    h1 = (1 - R ** 2) ** 0.5
    th = (3 ** 0.5)/2
    h2 = (th ** 2 - (R - r) ** 2) ** 0.5
    angles = np.linspace(0, np.pi * 2, 5, endpoint=False) + np.pi / 5
    x2 = np.cos(angles) * R
    y2 = np.sin(angles) * R
    vertices = np.zeros((12, 3))
    vertices[0, 2] = -h1 - h2/2
    vertices[1:6, 0] = x1
    vertices[1:6, 1] = y1
    vertices[1:6, 2] = - h2/2
    vertices[6:11, 0] = x2
    vertices[6:11, 1] = y2
    vertices[6:11, 2] = h2/2
    vertices[11, 2] = h1 + h2/2
    triangles = np.zeros((20, 3)).astype(int)
    triangles[:5, 0] = 0
    triangles[:5, 1] = [1, 2, 3, 4, 5]
    triangles[:5, 2] = [2, 3, 4, 5, 1]

    triangles[5:10, 1] = [1, 2, 3, 4, 5]
    triangles[5:10, 0] = [2, 3, 4, 5, 1]
    triangles[5:10, 2] = [6, 7, 8, 9, 10]

    triangles[10:15, 0] = [6, 7, 8, 9, 10]
    triangles[10:15, 1] = [7, 8, 9, 10, 6]
    triangles[10:15, 2] = [2, 3, 4, 5, 1]

    triangles[15:, 1] = [6, 7, 8, 9, 10]
    triangles[15:, 0] = [7, 8, 9, 10, 6]
    triangles[15:, 2] = 11
    return vertices, triangles


class Sphere(Mesh):
    def __init__(self, radius: float = 1.0, smoothness=1,
                 smooth=True, init_uv=False):
        vertices, triangles = get_icosahedron()
        super().__init__(vertices, triangles)
        self.flip_normals()
        for i in range(smoothness):
            self.subdivide2()

        vert_distances = np.linalg.norm(self.vertices, axis=1)
        self.vertices *= radius / vert_distances[:, None]
        if not smooth:
            self.flatten()
        self.normals = self.get_normals()
        if init_uv:
            self.init_uv()
        pass

    def init_uv(self):
        pitch = np.arcsin(self.vertices[:, 1])[:, None]
        yaw = np.arctan2(self.vertices[:, 0], self.vertices[:, 2])[:, None]
        self.uv = np.hstack((pitch/ np.pi + 0.5, yaw/np.pi/ 2 + 0.5))
