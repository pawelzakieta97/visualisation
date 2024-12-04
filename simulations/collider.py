import numpy as np

from models.mesh import Mesh
from raytracing.renderable import Renderable


class Collider:
    def __init__(self, mesh: Mesh, static=False):
        com = mesh.vertices.mean(axis=0)
        mesh.translate(translation=com)
        mesh.vertices -= com
        self.v = np.zeros(3, dtype=float)
        self.w = np.zeros(3, dtype=float)
        self.m = len(mesh.vertices)
        self.q = np.zeros(4)
        self.q[3]=1
        self.mesh = mesh
        self.normals = self.mesh.get_triangle_normals(self.mesh.vertices[self.mesh.triangle_indices, :], normalize=True)
        self.normal_vertices = self.mesh.vertices[self.mesh.triangle_indices[:, 0], :]
        unique_normals, unique_normal_idx = np.unique(self.normals, axis=0, return_index=True)
        self.normals = self.normals[unique_normal_idx, :]
        self.normal_vertices = self.normal_vertices[unique_normal_idx, :]
        self.normal_vertices = np.concatenate((self.normal_vertices, np.ones((self.normal_vertices.shape[0], 1))), axis=1)
        self.vertices = np.unique(self.mesh.vertices, axis=0)

        self.vertices = np.concatenate((self.vertices, np.ones((self.vertices.shape[0], 1))), axis=1)
        self.com = self.get_com()
        self.I = self.get_I()
        self.I_inv = 1/self.I
        self.world_vertices = None
        self.world_normals = None
        self.world_normal_vertices = None
        self.static = static

    def get_world_vertices(self):
        return (self.mesh.transformation @ self.vertices.T).T[:, :3]

    def get_world_normals(self):
        return (self.mesh.transformation[:3, :3] @ self.normals.T).T

    def get_world_normals_vertices(self):
        return (self.mesh.transformation @ self.normal_vertices.T).T[:, :3]

    def get_com(self):
        return self.mesh.vertices.mean(axis=0)

    def get_I_old(self):
        distances = self.vertices[:, :3]
        Ixx = (distances[:,1:]**2).sum()
        Iyy = (distances[:,[0,2]]**2).sum()
        Izz = (distances[:,:-1]**2).sum()
        Ixy = (distances[:,1] * distances[:,2]).sum()
        Ixz = (distances[:,0] * distances[:,2]).sum()
        Iyz = (distances[:,1] * distances[:,2]).sum()

        I = np.array([[Ixx, Ixy, Ixz],
                      [Ixy, Iyy, Iyz],
                      [Ixz, Iyz, Izz]])
        return I

    def get_I(self):
        distances_squared = (self.vertices[:, :3] ** 2).sum(axis=0)
        return np.array([distances_squared[[1,2]].sum(), distances_squared[[0,2]].sum(), distances_squared[[0,1]].sum()])

    def get_bb(self):
        return np.stack((self.mesh.vertices.min(axis=0), self.mesh.vertices.max(axis=0)))