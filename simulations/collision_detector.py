import numpy as np

from models.mesh import Mesh
from simulations.collider import Collider


class CollisionDetector:
    def __init__(self, meshes: list[Mesh]):
        self.meshes = meshes

    def get_collisions(self):
        pass


def get_collisions(c1, c2):
    for c in [c1, c2]:
        c.world_vertices = c.get_world_vertices()
        c.world_normals = c.get_world_normals()
        c.world_normal_vertices = c.get_world_normals_vertices()
    plane_heights = (c1.world_normals * c1.world_normal_vertices).sum(axis=-1, keepdims=True)
    vertex_plane_distances = np.dot(c1.world_normals, c2.world_vertices.T) - plane_heights
    vertex_plane_distances_max = vertex_plane_distances.max(axis=0)

    # always return only the max collision depth????
    collision_vertex_idx = vertex_plane_distances_max.argmin()
    if vertex_plane_distances_max[collision_vertex_idx] >= 0:
        return None
    collision_plane_idx = vertex_plane_distances[:, collision_vertex_idx].argmax()
    collision_depth = vertex_plane_distances[collision_plane_idx, collision_vertex_idx]
    p2 = c2.world_vertices[collision_vertex_idx, :]
    p1 = p2 - c1.world_normals[collision_plane_idx, :] * collision_depth
    return p1, p2, collision_depth
