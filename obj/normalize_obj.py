import os

import numpy as np

from models.parse_obj import parse_obj

if __name__ == '__main__':
    size = 5
    for file in os.listdir('.'):
        if not file.endswith('.obj') or file.endswith('normalized.obj'):
            continue
        vertices, triangles = parse_obj(file)
        used_mask = np.zeros(vertices.shape[0], dtype=bool)
        used_mask[np.unique(triangles.flatten())] = 1

        filtered_vertices = vertices[used_mask, :]
        mins = filtered_vertices.min(axis=0)
        maxs = filtered_vertices.max(axis=0)
        sizes = maxs - mins

        center = (mins + maxs) / 2
        vertices_centered = vertices - center[None, :]
        vertices_centered /= sizes.max()/size
        filtered_vertices = filtered_vertices - center[None, :]
        filtered_vertices /= sizes.max()/size
        vertices_centered[:, 1] -= filtered_vertices[:, 1].min()
        with open(file[:-4] + '_normalized.obj', 'w+') as f:
            f.writelines(['v ' + ' '.join([str(v) for v in vertex]) + '\n' for vertex in vertices_centered.tolist()])
            f.writelines(['f ' + ' '.join([str(v+1) for v in triangle]) + '\n' for triangle in triangles.tolist()])