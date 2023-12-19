from typing import Sequence, Union

import numpy as np

from transformations import get_rotation_matrix_x, get_translation_matrix


class Mesh:
    def __init__(self, vertices: np.array, triangle_indices: np.array = None,
                 color: np.array = None, normals=None, uv: np.array = None):
        if vertices.shape[1] == 2:
            vertices = np.concatenate((vertices, np.zeros((vertices.shape[0], 1))), axis=1)
        if triangle_indices is None:
            triangle_indices = np.arange(vertices.shape[0]).reshape(-1, 3)

        self.triangle_indices = triangle_indices
        self.color: np.array = color
        self.uv = uv
        self.vertices = vertices
        if normals is None:
            normals = self.get_normals()

        self.normals = normals
        self.edges, self.triangle_edges = None, None
        self.transformation = np.eye(4)
        self.changed = True

    def copy(self):
        color = self.color.copy() if self.color is not None else None
        uv = self.uv.copy() if self.uv is not None else None
        return Mesh(vertices=self.vertices.copy(),
                    triangle_indices=self.triangle_indices.copy(),
                    color=color, normals=self.normals, uv=uv)

    def flip_normals(self):
        self.triangle_indices[:, [0,1]] = self.triangle_indices[:, [1,0]]
        self.normals = self.get_normals()

    def get_edges(self):
        all_edges = np.hstack((self.triangle_indices[:, :2],
                               self.triangle_indices[:, 1:],
                               self.triangle_indices[:, (2, 0)])).reshape(-1, 2)
        all_edges, triangle_to_edge = np.unique(np.sort(all_edges, axis=1), axis=0, return_inverse=True)
        triangle_edges = triangle_to_edge.reshape(-1, 3)
        # triangle_normals = self.get_triangle_normals(normalize=False)
        # triangle_edge_vertexes = self.vertices[all_edges[triangle_edges]]
        # a = triangle_edge_vertexes[:, 1, 0, :] - triangle_edge_vertexes[:, 0, 0, :]
        # b = triangle_edge_vertexes[:, 2, 0, :] - triangle_edge_vertexes[:, 0, 0, :]
        # new_normals = np.cross(a, b)
        return all_edges, triangle_edges

    def get_edge_lengths(self):
        if self.edges is None or self.triangle_edges is None:
            self.edges, self.triangle_edges = self.get_edges()
        return np.linalg.norm(self.vertices[self.edges[:, 1], :] - self.vertices[self.edges[:, 0], :], axis=1)

    @staticmethod
    def get_triangle_normals(triangle_vertices, normalize=True):
        # triangle_vertices = self.vertices[self.triangle_indices, :]
        a = triangle_vertices[:, 1, :] - triangle_vertices[:, 0, :]
        b = triangle_vertices[:, 2, :] - triangle_vertices[:, 0, :]
        res = np.cross(a, b)
        if normalize:
            return res / np.linalg.norm(res, axis=1)[:, None]
        return res

    def get_normals(self):
        normals = self.get_triangle_normals(self.vertices[self.triangle_indices, :], normalize=False)
        vertex_normals = np.zeros_like(self.vertices)
        for idx, (normal, triangle_idx) in enumerate(zip(normals, self.triangle_indices)):
            vertex_normals[triangle_idx, :] += normal
        return vertex_normals / np.linalg.norm(vertex_normals, axis=1)[:, None]

    def transform_mesh(self, transform_matrix):
        self.vertices = transform_matrix.dot(np.hstack(
            (self.vertices, np.ones((self.vertices.shape[0], 1)))
        ).T).T[:, :-1]

    def transform(self, transform_matrix):
        self.transformation = self.transformation @ transform_matrix

    def flatten(self):
        new_vertices = self.vertices[self.triangle_indices, :].reshape(-1, 3)
        new_indices = np.arange(len(self.triangle_indices) * 3).reshape(-1, 3)
        self.vertices = new_vertices
        self.triangle_indices = new_indices
        self.normals = self.get_normals()

    def subdivide(self, edge_index):
        if self.edges is None or self.triangle_edges is None:
            self.edges, self.triangle_edges = self.get_edges()
        adjacent_triangles = np.argwhere(self.triangle_edges == edge_index)[:, 0]
        edge_vertex_indexes = self.edges[edge_index, :]
        new_point = self.vertices[edge_vertex_indexes, :].mean(axis=0)
        new_color = self.color[edge_vertex_indexes, :].mean(axis=0) if self.color is not None else None
        new_normal = self.normals[edge_vertex_indexes, :].mean(axis=0)
        new_point_index = self.vertices.shape[0]
        self.vertices = np.append(self.vertices, new_point[None, :], axis=0)
        self.color = np.append(self.color, new_color[None, :], axis=0) if self.color is not None else None
        self.normals = np.append(self.normals, new_normal[None, :], axis=0)
        for adjacent_triangle_index in adjacent_triangles:
            adjacent_triangle = self.triangle_indices[adjacent_triangle_index, :]
            opposite_point = [p for p in adjacent_triangle if p not in edge_vertex_indexes][0]
            opposite_point_index_in_triangle = np.argwhere(adjacent_triangle == opposite_point)[0, 0]
            a_point_index_in_triangle = np.argwhere(adjacent_triangle == edge_vertex_indexes[0])[0, 0]
            triangle_dir = (a_point_index_in_triangle - opposite_point_index_in_triangle) % 3 == 1
            if triangle_dir:
                new_triangle1_indexes = np.array([new_point_index, opposite_point, edge_vertex_indexes[0]])
                new_triangle2_indexes = np.array([new_point_index, edge_vertex_indexes[1], opposite_point])
            else:
                new_triangle1_indexes = np.array([new_point_index, edge_vertex_indexes[0], opposite_point])
                new_triangle2_indexes = np.array([new_point_index, opposite_point, edge_vertex_indexes[1]])
            self.triangle_indices[adjacent_triangle_index, :] = new_triangle1_indexes
            self.triangle_indices = np.vstack((self.triangle_indices,
                                               new_triangle2_indexes[None, :]))
        self.edges, self.triangle_edges = self.get_edges()

    @staticmethod
    def edge_id(a, b):
        return (str((a, b)), False) if b > a else (str((b, a)), True)

    def subdivide2(self):
        new_vertices = {}
        vertices = self.vertices.copy()
        triangle_indices = np.zeros((4*self.triangle_indices.shape[0], 3))
        for i, triangle in enumerate(self.triangle_indices):
            t1, t2, t3 = triangle
            for a, b in zip([t1,t2,t3], [t2,t3,t1]):
                edge_id, reverse = self.edge_id(a, b)
                if edge_id in new_vertices:
                    continue
                new_point = (self.vertices[a, :] + self.vertices[b, :])/2
                new_vertices[edge_id] = vertices.shape[0]
                vertices = np.vstack((vertices, new_point[None, :]))

        for i, triangle in enumerate(self.triangle_indices):
            t1, t2, t3 = triangle
            # center triangle
            for en, (a, b) in enumerate(zip([t1,t2,t3], [t2,t3,t1])):
                edge_id, reverse = self.edge_id(a, b)
                triangle_indices[4*i, en] = new_vertices[edge_id]
            # side triangles
            for en, (a, b, c) in enumerate(zip([t1, t2, t3], [t2, t3, t1], [t3, t1, t2])):
                edge_id1, reverse = self.edge_id(a, b)
                edge_id2, reverse = self.edge_id(b, c)
                triangle_indices[4*i + en + 1, 0] = new_vertices[edge_id1]
                triangle_indices[4*i + en + 1, 1] = b
                triangle_indices[4*i + en + 1, 2] = new_vertices[edge_id2]

        self.triangle_indices = triangle_indices.astype(int)
        self.vertices = vertices
        self.normals = self.get_normals()
        self.changed = True
        pass

    def set_position(self, position):
        self.transformation[:3, 3] = np.array(position)
        self.changed = True



def get_rect(segments_x, segments_y, seg_size):
    xs, ys = np.meshgrid(np.arange(0, segments_x) * seg_size, np.arange(0, segments_y) * seg_size)
    vertices = np.concatenate((xs.reshape(-1, 1), ys.reshape(-1, 1)), axis=1)
    grid_indexes = np.arange(segments_x * segments_y).reshape(segments_y, segments_x)
    t1a = grid_indexes[:-1, :-1].reshape(-1, 1)
    t1b = grid_indexes[:-1, 1:].reshape(-1, 1)
    t1c = grid_indexes[1:, :-1].reshape(-1, 1)

    t2a = grid_indexes[1:, 1:].reshape(-1, 1)
    t2b = grid_indexes[1:, :-1].reshape(-1, 1)
    t2c = grid_indexes[:-1, 1:].reshape(-1, 1)

    triangle_indexes = np.vstack(
        (
            np.hstack((t1a, t1b, t1c)),
            np.hstack((t2a, t2b, t2c))
        )
    )
    colors = np.ones((vertices.shape[0], 3)) * 0.3
    return Mesh(vertices, triangle_indexes, color=colors)


def get_grid(segments_x, segments_y, seg_size):
    xs, ys = np.meshgrid(np.arange(0, segments_x) * seg_size, np.arange(0, segments_y) * seg_size)
    vertices = np.concatenate((xs.reshape(-1, 1), ys.reshape(-1, 1)), axis=1)[:, None, :]
    deltas = np.array([[0, 0],
                       [seg_size, 0],
                       [seg_size, seg_size],
                       [0, seg_size]])
    quads = vertices + deltas[None, :, :]
    quad_indexes = np.arange(len(quads))
    quad_idx_x = quad_indexes % segments_y
    quad_idx_y = quad_indexes // segments_x

    colors = ((quad_idx_x + quad_idx_y) % 2 == 0)[:, None, None] * np.ones((1, 4, 3)) * 0.5 + 0.25
    triangles_indexes = np.array([[0, 1, 2], [2, 3, 0]])
    triangles_indexes = (np.arange(quads.shape[0]) * 4)[:, None, None] + triangles_indexes[None, :, :]
    triangles_indexes = triangles_indexes.reshape(-1, 3)
    vertices = quads.reshape(-1, 2)
    colors = colors.reshape(-1, 3)
    grid = Mesh(vertices, triangles_indexes, color=colors)
    grid.transform_mesh(get_rotation_matrix_x(-np.pi / 2))
    grid.transform_mesh(get_translation_matrix(dx=-5))
    return grid


def get_cube(pos: np.array = None, size: Union[float, Sequence] = 1.0, smooth=True):
    points = np.array([[0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1],
                           [0, 1, 0], [1, 1, 0], [1, 1, 1], [0, 1, 1]]).astype(float)
    if pos is None:
        pos = np.zeros(3)
    points += pos[None, :]
    if isinstance(size, float) or isinstance(size, int):
        size = np.ones(3) * size
    points *= size[None, :]
    bottom_triangles = np.array([[0, 1, 2], [2, 3, 0]])
    # 6, 5, 4, 7
    top_triangles = np.array([[6, 5, 4], [4, 7, 6]])
    # 4, 5, 1, 0
    front_triangles = np.array([[4, 5, 1], [1, 0, 4]])
    # 6, 7, 3, 2
    back_triangles = np.array([[6, 7, 3], [3, 2, 6]])
    # 0, 3, 7, 4
    left_triangles = np.array([[0, 3, 7], [7, 4, 0]])
    # 2, 1, 5, 6
    right_triangles = np.array([[2, 1, 5], [5, 6, 2]])
    triangle_indices = np.concatenate((bottom_triangles,
                                       top_triangles,
                                       front_triangles,
                                       back_triangles,
                                       left_triangles,
                                       right_triangles))
    colors = np.ones(points.shape)
    colors[0, 1:] = 0
    return Mesh(points, triangle_indices, colors)


def get_sphere(pos: np.array = None, radius: float=1, vert_count=14):
    sphere = get_cube(pos, 1.0, True)
    for i in range(vert_count - 8):
        max_edge = np.argmax(sphere.get_edge_lengths())
        sphere.subdivide(max_edge)
    vert_distances = np.linalg.norm(sphere.vertices - 0.5, axis=1)
    sphere.vertices = 0.5 + (sphere.vertices - 0.5) / vert_distances[:, None]
    sphere.normals = sphere.get_normals()
    return sphere


if __name__ == '__main__':
    cube = get_cube(0,0,True)
    edges = cube.get_edges()
    cube.subdivide(0)
