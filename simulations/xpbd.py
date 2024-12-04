import numpy as np

from simulations.collider import Collider
from transformations import rotation_matrix_to_quaternion, quaternion_multiply, quaternion_to_rotation_matrix


class XPBD:
    def __init__(self, objects: list[Collider], dt=1/60, substeps=20, g=None):
        self.objects = objects
        if g is None:
            g = np.array([0, -9.81, 0]) * 0.00001
        self.g = g
        self.dt = dt
        self.substeps = substeps

    def step(self):
        h = self.dt / self.substeps
        for ss in range(self.substeps):
            for obj in self.objects:
                prev_pos = obj.mesh.transformation[:3, -1].copy()
                obj.v += self.g * h
                obj.mesh.transformation[:3, -1] += obj.v * h
                obj.w += h * 0.5 * obj.I_inv * (-np.cross(obj.w, obj.I * obj.w))
                q = rotation_matrix_to_quaternion(obj.mesh.transformation)
                q_prev = q.copy()
                q += 0.5 * h * quaternion_multiply([obj.w[0], obj.w[1], obj.w[2], 0], q)
                q /= np.linalg.norm(q)
                obj.mesh.transformation[:3, :3] = quaternion_to_rotation_matrix(q)
                print(q)
                pass
                # prev_orientation = obj.mesh.transformation[:3, :3].copy()
                # """https://physics.stackexchange.com/questions/293037/how-to-compute-the-angular-velocity-from-the-angles-of-a-rotation-matrix"""
                # dM = np.array([[1, -obj.w[2], obj.w[1]],
                #                [obj.w[2], 1, -obj.w[0]],
                #                [-obj.w[1], obj.w[0], 1]])
                # obj.mesh.transformation[:3, :3] = obj.mesh.transformation[:3, :3] @ dM
                # # projection to valid rotation matrix
                # """https://stackoverflow.com/questions/23080791/eigen-re-orthogonalization-of-rotation-matrix"""
                # M = obj.mesh.transformation[:3, :3]
                # obj.mesh.transformation[:3, :3] = 0.5*(np.linalg.inv(M.T) + M)


