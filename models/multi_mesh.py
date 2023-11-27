import numpy as np

from models.mesh import Mesh
from models.primitives.cube import Cube


class MultiMesh(Mesh):
    def __init__(self, reference_mesh: Mesh, transformations: np.array = None, count: int = 10):
        if transformations is None:
            transformations = np.stack([np.eye(4)] * count)
        self.count = transformations.shape[0]
        self.vert_count = reference_mesh.vertices.shape[0]
        base_vertices = np.stack([reference_mesh.vertices] * self.count)
        base_normals = np.stack([reference_mesh.normals] * self.count)
        indices = np.stack([reference_mesh.triangle_indices] * self.count) + (np.arange(self.count) * self.vert_count)[
                                                                             :, None, None]
        super().__init__(base_vertices.reshape(-1, 3),
                         indices.reshape(-1, 3),
                         normals=base_normals.reshape(-1, 3))
        self.base_vertices = np.transpose(base_vertices, (0, 2, 1))
        self.base_normals = np.transpose(base_normals, (0, 2, 1))
        self.transform_mesh(transformations)
        self.changed = True

    def transform_mesh(self, transformations: np.array):
        uniform_verts = np.concatenate((self.base_vertices, np.ones((self.count, 1, self.vert_count))), axis=1)
        self.vertices = (transformations @ uniform_verts).transpose((0, 2, 1))[:,:,:-1].reshape(-1, 3)
        # TODO: fix normals transformations (works for translation and rotation, breaks for non-uniform scaling)
        self.normals = (transformations[:, :-1, :-1] @ self.base_normals).transpose((0, 2, 1)).reshape(-1, 3)
        self.changed = True
        pass

    def set_positions(self, positions: np.array):
        self.vertices = (self.base_vertices + positions[:, :, None]).transpose((0, 2, 1)).reshape(-1, 3)
        self.changed = True


def merge_meshes(objects: list[Mesh]):
    vert_counts = [len(obj.vertices) for obj in objects]
    triangle_indices_count = [len(obj.triangle_indices) for obj in objects]
    merged_verts = np.zeros((sum(vert_counts), 3))
    merged_colors = np.zeros_like(merged_verts)
    merged_normals = np.zeros_like(merged_verts)
    merged_triangle_indices = np.zeros((sum(triangle_indices_count), 3)).astype(int)
    first_vert_index = 0
    first_tri_index = 0
    for obj in objects:
        last_vert_index = first_vert_index + len(obj.vertices)
        last_tri_index = first_tri_index + len(obj.triangle_indices)
        merged_verts[first_vert_index: last_vert_index, :] = obj.vertices
        if obj.color is None:
            merged_colors = None
        if merged_colors is not None:
            merged_colors[first_vert_index: last_vert_index, :] = obj.color
        merged_normals[first_vert_index: last_vert_index, :] = obj.normals
        merged_triangle_indices[first_tri_index: last_tri_index, :] = obj.triangle_indices + first_vert_index
        first_vert_index = last_vert_index
        first_tri_index = last_tri_index
    return merged_verts, merged_triangle_indices, merged_colors, merged_normals
    return Mesh(merged_verts, merged_triangle_indices, merged_colors, merged_normals)


if __name__ == '__main__':
    ref_mesh = Cube()
    mm = MultiMesh(ref_mesh, count=10)
