import time

import numpy as np

from models.parse_obj import parse_obj
from raytracing.bvh import get_object_tree_greedy
from raytracing.camera import Camera
from raytracing.group import Group
from raytracing.renderable import Renderable
from raytracing.renderer import hits_triangle, hit3, INF_DISTANCE
from raytracing.triangle import Triangle

def render(objects: list[Renderable], camera: Camera):
    bvh = get_object_tree_greedy(objects, max_objs_per_bb=2)
    # bvh = bvh.elements[0]
    group_child_types, group_child_indexes, group_bbs, children_data = bvh.serialize()
    types_map = {
        Group: 0,
        Triangle: 2,
        -1: -1
    }
    group_bbs = np.array(group_bbs)
    group_child_types = np.array([[types_map[c] for c in child_types] for child_types in group_child_types])
    triangles_data = children_data[Triangle]
    triangles_data = np.array(triangles_data)
    group_child_indexes = np.array(group_child_indexes)
    rays = camera.get_rays()

    start = time.time()
    res = hit3(rays, group_bbs, group_child_indexes, group_child_types, triangles_data)
    return res
    ray_count = rays[0].shape[0]
    ray_starts = rays[0]
    ray_directions = rays[1]
    triangles_normals = triangles_data[:, 12:15]
    triangles_Ts = triangles_data[:, :12].reshape(-1, 3, 4)
    triangles_h = triangles_data[:, 15]
    min_distances = np.ones(ray_count) * INF_DISTANCE
    ids = np.zeros(ray_count)
    for i, (T, normal, h) in enumerate(zip(triangles_Ts, triangles_normals, triangles_h)):
        distances = hits_triangle(ray_starts, ray_directions, np.stack([T] * ray_count), np.stack([normal] * ray_count), np.ones(ray_count) * h)
        closer_mask = distances < min_distances
        min_distances[closer_mask] = distances[closer_mask]
        ids[closer_mask] = i + 1
    print(time.time() - start)
    return ids


if __name__ == "__main__":
    vertices, triangles = parse_obj('../obj/bunny.obj')
    vertices = vertices * 20

    triangles1 = [Triangle(vertices[triangle]) for triangle in triangles]
    triangle_count = 10
    triangles = [Triangle(np.array([[i, 0, 0],
                                    [i+1, 0, 0],
                                    [i, 1, 0]])) for i in range(triangle_count)]
    depth_stack = 10
    for i in range(depth_stack):
        triangles += [Triangle(t.data - np.array([[0,0,1],[0,0,1],[0,0,1]])) for t in triangles[-10:]]
    width = 1000
    height = 1000
    camera = Camera(width=width, height=height,
                    position=np.array([triangle_count/2, 2, triangle_count/2]), yaw=0)
    camera = Camera(width=width, height=height,
                    position=np.array([0,2,5]), yaw=0)
    res = render(triangles1, camera)
    res = ((res.reshape(height, width))[::-1, :] + 1 )/ triangle_count
    pass