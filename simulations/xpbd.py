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
                obj.w += h * obj.I_inv * (-np.cross(obj.w, obj.I * obj.w))
                w1, w2, w3 = obj.w
                I1, I2, I3 = obj.I

                # obj.w += np.array([(I2-I3)*w2*w3/I1, (I3-I1)*w1*w3/I2, (I1-I2)*w1*w2/I3]) * h
                # dw1 = h * 0.5 * 1/I1 * - (w2I3w3 - w3I2w2) = h * 0.5 * 1/I1 * w2 * w3 * (I2 - I3)

                # TODO: find some more elegant way to update transformation matrix.
                #  Currently the rotation matrix is converted to a quaternion,
                #  quaternion is updated with rotational velocity and converted back to rotation matrix
                q = rotation_matrix_to_quaternion(obj.mesh.transformation)
                q_prev = q.copy()

                q += 0.5 * h * quaternion_multiply(q, [obj.w[0], obj.w[1], obj.w[2], 0])
                q /= np.linalg.norm(q)
                obj.mesh.transformation[:3, :3] = quaternion_to_rotation_matrix(q)
