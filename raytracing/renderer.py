from __future__ import annotations
import pickle
import time

import numpy as np

from raytracing.group import Group

from raytracing.bvh import get_object_tree_fast, hit_triangle_bvh, get_object_tree_greedy
from raytracing.camera import Camera
from raytracing.renderable import Renderable
from raytracing.triangle import Triangle
from raytracing.sphere import Sphere

np.random.seed(2)


def render(objects: list[Renderable], camera: Camera):
    start = time.time()
    bvh = get_object_tree_fast(objects, max_objs_per_bb=2)
    print('BVH generated')
    print(time.time() - start)
    pickle.dump(bvh, open("bvh.p", "wb"))
    def _get_max_depth(bvh: Group, start=0) -> int:
        if not isinstance(bvh, Group):
            return start
        return max([_get_max_depth(child, start+1) for child in bvh.elements])

    def _get_group_count(bvh: Group) -> int:
        if not isinstance(bvh, Group):
            return 0
        return sum([_get_group_count(child) for child in bvh.elements]) + 1
    print(_get_max_depth(bvh))
    print(_get_group_count(bvh))
    # bvh = bvh.elements[0]
    group_child_types, group_child_indexes, group_bbs, children_data = bvh.serialize()
    group_bbs = np.array(group_bbs)
    group_child_types = np.array([[c.get_type_id() if c!=-1 else -1 for c in child_types] for child_types in group_child_types])
    triangles_data = children_data[Triangle]
    triangles_data = np.array(triangles_data)
    group_child_indexes = np.array(group_child_indexes)
    rays = camera.get_rays()

    res = hit_triangle_bvh(rays, group_bbs, group_child_indexes, group_child_types, triangles_data)
    return res

if __name__ == '__main__':
    s = Sphere()
    t = Triangle(np.random.random((3,3)))
    print(s.get_type_id())
    print(t.get_type_id())
    print(s.get_type_id())