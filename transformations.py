import numpy as np


def get_translation_matrix(dx=0, dy=0, dz=0, translation=None):
    t = np.eye(4)
    if translation is not None:
        translation_vector = translation
    else:
        translation_vector = np.array([dx, dy, dz])
    t[:-1, -1] = translation_vector
    return t

def get_rotation_matrix_x(angle):
    return np.array([[1, 0,             0,              0],
                     [0, np.cos(angle), -np.sin(angle), 0],
                     [0, np.sin(angle), np.cos(angle),  0],
                     [0, 0,             0,              1]])


def get_rotation_matrix_y(angle):
    return np.array([[np.cos(angle),    0, np.sin(angle),   0],
                     [0,                1, 0,               0],
                     [-np.sin(angle),   0, np.cos(angle),   0],
                     [0,                0, 0,               1]])


def get_rotation_matrix_z(angle):
    return np.array([[np.cos(angle),    -np.sin(angle), 0, 0],
                     [np.sin(angle),    np.cos(angle),  0, 0],
                     [0,                0,              1, 0],
                     [0,                0,              0, 1]])


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

def get_projection_matrix(fov, aspect_ratio, near=0.1, far=1000):
    projection_matrix = np.zeros((4,4))
    S = 1 / np.tan(fov/2)
    projection_matrix[1, 1] = S
    projection_matrix[0, 0] = S / aspect_ratio
    projection_matrix[2, 2] = - (far+near) / (far - near)
    projection_matrix[3, 2] = -1
    projection_matrix[2, 3] = - (2 * far * near) / (far - near)
    return projection_matrix



if __name__ == '__main__':
    trans = look_at([0, 0, 0], [1, 0, 1])
    pass