import numpy as np


def parse_obj(obj_file_path: str):
    vertices = []
    triangle_indexes = []
    for line in open(obj_file_path).readlines():
        if line.startswith('v'):
            vertices.append([float(v) for v in line.split()[1:]])
        if line.startswith('f'):
            triangle_indexes.append([int(v) for v in line.split()[1:]])
    return np.array(vertices), np.array(triangle_indexes) - 1