import numpy as np


def get_translation_matrix(dx=0, dy=0, dz=0, translation=None):
    t = np.eye(4)
    if translation is not None:
        translation_vector = translation
    else:
        translation_vector = np.array([dx, dy, dz])
    t[:-1, -1] = translation_vector
    return t


def get_scale_matrix(sx=1, sy=1, sz=1, scale=None):
    t = np.eye(4)
    if scale is None:
        scale = [sx, sy, sz]
    t[[0, 1, 2], [0, 1, 2]] = scale
    return t


def get_rotation_matrix_x(angle):
    return np.array([[1, 0, 0, 0],
                     [0, np.cos(angle), -np.sin(angle), 0],
                     [0, np.sin(angle), np.cos(angle), 0],
                     [0, 0, 0, 1]])


def get_rotation_matrix_y(angle):
    return np.array([[np.cos(angle), 0, np.sin(angle), 0],
                     [0, 1, 0, 0],
                     [-np.sin(angle), 0, np.cos(angle), 0],
                     [0, 0, 0, 1]])


def get_rotation_matrix_z(angle):
    return np.array([[np.cos(angle), -np.sin(angle), 0, 0],
                     [np.sin(angle), np.cos(angle), 0, 0],
                     [0, 0, 1, 0],
                     [0, 0, 0, 1]])


def look_at(position: np.array, target: np.array = None, yaw: float = None,
            pitch=None, up: np.array = None):
    position = np.array(position)
    if target is None:
        return get_translation_matrix(*position) @ get_rotation_matrix_y(yaw) @ get_rotation_matrix_x(pitch)
    target = np.array(target)
    if up is None:
        up = np.array([0, 1, 0])
    up = np.array(up)
    forward = target - position
    forward = forward / np.linalg.norm(forward)
    right = np.cross(forward, up)
    right = right / np.linalg.norm(right)

    up = np.cross(right, forward)
    transformation = np.eye(4)
    transformation[:-1, 0] = right
    transformation[:-1, 1] = up
    transformation[:-1, 2] = -forward
    transformation[:-1, 3] = position
    return transformation


def get_perspective_projection_matrix(fov, aspect_ratio, near=0.1, far=1000, zoom=1):
    projection_matrix = np.zeros((4, 4))
    S = 1 / np.tan(fov / 2) * zoom
    projection_matrix[1, 1] = S
    projection_matrix[0, 0] = S / aspect_ratio
    projection_matrix[2, 2] = - (far + near) / (far - near)
    projection_matrix[3, 2] = -1
    projection_matrix[2, 3] = - (2 * far * near) / (far - near)
    return projection_matrix


def get_orthographic_projection_matrix(scale, aspect_ratio, near=0.1, far=1000):
    orthogonal_matrix = np.zeros((4, 4))
    orthogonal_matrix[1, 1] = scale * far
    orthogonal_matrix[0, 0] = scale / aspect_ratio * far
    orthogonal_matrix[2, 2] = - 1
    orthogonal_matrix[3, 3] = far
    return orthogonal_matrix


def levels(image: np.array, low: float = 0, high: float = 1):
    result = image * (high - low) + low * 255
    result[result<0] = 0
    result[result>255] = 255
    return result


def quaternion_to_rotation_matrix(Q: np.array) -> np.array:
    """
    Covert a quaternion into a full three-dimensional rotation matrix.

    Input
    :param Q: A 4 element array representing the quaternion (q0,q1,q2,q3)

    Output
    :return: A 3x3 element matrix representing the full 3D rotation matrix.
             This rotation matrix converts a point in the local reference
             frame to a point in the global reference frame.
    """
    # Extract the values from Q
    q0 = Q[3]
    q1 = Q[0]
    q2 = Q[1]
    q3 = Q[2]

    # First row of the rotation matrix
    r00 = 2 * (q0 * q0 + q1 * q1) - 1
    r01 = 2 * (q1 * q2 - q0 * q3)
    r02 = 2 * (q1 * q3 + q0 * q2)

    # Second row of the rotation matrix
    r10 = 2 * (q1 * q2 + q0 * q3)
    r11 = 2 * (q0 * q0 + q2 * q2) - 1
    r12 = 2 * (q2 * q3 - q0 * q1)

    # Third row of the rotation matrix
    r20 = 2 * (q1 * q3 - q0 * q2)
    r21 = 2 * (q2 * q3 + q0 * q1)
    r22 = 2 * (q0 * q0 + q3 * q3) - 1

    # 3x3 rotation matrix
    rot_matrix = np.array([[r00, r01, r02],
                           [r10, r11, r12],
                           [r20, r21, r22]])

    return rot_matrix

def rotation_matrix_to_quaternion(m: np.array) -> np.array:
    m = m.T
    if m[2,2] < 0:
        if m[0,0] > m[1,1]:
            t = 1 + m[0,0] -m[1,1] -m[2,2]
            q = np.array( [t, m[0,1]+m[1,0], m[2,0]+m[0,2], m[1,2]-m[2,1]] )
        else:
            t = 1 -m[0,0] + m[1,1] -m[2,2]
            q = np.array( [m[0,1]+m[1,0], t, m[1,2]+m[2,1], m[2,0]-m[0,2]] )
    else:
        if m[0,0] < -m[1,1]:
            t = 1 -m[0,0] -m[1,1] + m[2,2]
            q = np.array( [m[2,0]+m[0,2], m[1,2]+m[2,1], t, m[0,1]-m[1,0]])
        else:
            t = 1 + m[0,0] + m[1,1] + m[2,2]
            q = np.array( [m[1,2]-m[2,1], m[2,0]-m[0,2], m[0,1]-m[1,0], t ])
    q *= 0.5 / np.sqrt(t)
    return q

def quaternion_multiply(quaternion1, quaternion0):
    x0, y0, z0, w0 = quaternion0
    x1, y1, z1, w1 = quaternion1
    return np.array([-x1 * x0 - y1 * y0 - z1 * z0 + w1 * w0,
                     x1 * w0 + y1 * z0 - z1 * y0 + w1 * x0,
                     -x1 * z0 + y1 * w0 + z1 * x0 + w1 * y0,
                     x1 * y0 - y1 * x0 + z1 * w0 + w1 * z0], dtype=np.float64)

if __name__ == '__main__':
    trans = get_orthographic_projection_matrix(200, 1.6)
    pass
