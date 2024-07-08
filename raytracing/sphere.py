import numpy as np

from raytracing.renderable import Renderable, INF_DISTANCE


class Sphere(Renderable):
    def __init__(self, pos: np.array = None, radius: float = 1):
        super().__init__()
        if pos is None:
            pos = np.zeros(3)
        self.pos = pos
        self.radius = radius

    def get_bb(self):
        return self.pos[None, :] + np.array([-1, 1])[:, None] * self.radius

    def serialize(self):
        return np.concatenate((self.pos, [self.radius]))


def hits_sphere(ray_starts, ray_directions, spheres_pos, spheres_r):
    if len(ray_starts) == 0:
        return spheres_r
    dp = spheres_pos - ray_starts
    a = (ray_directions * ray_directions).sum(axis=1)
    b = - 2 * (dp * ray_directions).sum(axis=1)
    c = (dp * dp).sum(axis=1) - spheres_r * spheres_r
    delta = b * b - 4 * a * c
    distances = np.ones_like(spheres_r, dtype=float) * INF_DISTANCE
    # normals = np.zeros_like(ray_starts, dtype=float)
    hits = delta > 0
    hit_distances = (-b[hits] - np.sqrt(delta[hits])) / (2 * a[hits])
    distances[hits] = hit_distances
    # normals[hits] = ray_starts[hits, :] + ray_directions[hits, :] * hit_distances[:, None]
    return distances

