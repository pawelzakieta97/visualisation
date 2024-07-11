import numpy as np
import torch

from raytracing.renderable import Renderable, INF_DISTANCE, MIN_DISTANCE


class Triangle(Renderable):
    def __init__(self, data: np.array):
        super().__init__()
        self.data = data
        a = data[1, :] - data[0, :]
        b = data[2, :] - data[1, :]
        normal = np.cross(a, b)
        self.normal = normal / np.linalg.norm(normal)
        T = data.T
        T = np.concatenate((T, np.ones((1, 3))))
        self. T = np.linalg.inv(T.T @ T) @ T.T
        self.h = np.dot(self.normal, data[0, :])

    def get_bb(self):
        return np.stack((self.data.min(axis=0), self.data.max(axis=0)))

    def serialize(self):
        return np.concatenate((self.T.flatten(), self.normal, [self.h]))


def hits_triangle(ray_starts, ray_directions, triangles_Ts, triangles_normals, triangles_h):
    # normals = triangles_data[:, 12:]
    # Ts = triangles_data[:, :12].reshape(-1, 3, 4)

    hit_distances = (triangles_h - (ray_starts * triangles_normals).sum(axis=-1)) / (ray_directions * triangles_normals).sum(axis=-1)
    hit_points = ray_starts + ray_directions * hit_distances[:, None]
    ws = triangles_Ts @ np.concatenate((hit_points, np.ones((hit_points.shape[0], 1))), axis=-1)[:,:, None]
    ws = ws[:,:,0]
    hits = np.bitwise_and((ws <= 1),(ws >= 0)).all(axis=-1)
    distances = np.ones(ray_starts.shape[0]) * INF_DISTANCE
    distances[hits] = hit_distances[hits]
    distances[distances < MIN_DISTANCE] = INF_DISTANCE
    return distances


def hits_triangle_torch(ray_starts, ray_directions, triangles_Ts, triangles_normals, triangles_h):
    # normals = triangles_data[:, 12:]
    # Ts = triangles_data[:, :12].reshape(-1, 3, 4)
    device = ray_starts.device
    hit_distances = (triangles_h - (ray_starts * triangles_normals).sum(axis=-1)) / (ray_directions * triangles_normals).sum(axis=-1)
    hit_points = ray_starts + ray_directions * hit_distances[:, None]
    ws = triangles_Ts @ torch.concatenate((hit_points, torch.ones((hit_points.shape[0], 1)).to(device)), axis=-1)[:,:, None]
    ws = ws[:,:,0]
    hits = torch.bitwise_and((ws <= 1),(ws >= 0)).all(axis=-1)
    distances = torch.ones(ray_starts.shape[0]).to(device) * INF_DISTANCE
    distances[hits] = hit_distances[hits]
    distances[distances < MIN_DISTANCE] = INF_DISTANCE
    return distances
