import time

import numpy as np

from models.parse_obj import parse_obj
from models.primitives.cube import Cube
from raytracing.bvh import get_object_tree_greedy
from raytracing.camera import Camera
from raytracing.group import Group
from raytracing.renderable import Renderable
from raytracing.renderer import hits_triangle, hit3, INF_DISTANCE
from raytracing.triangle import Triangle
import pickle

def render(objects: list[Renderable], camera: Camera):
    bvh = get_object_tree_greedy(objects, max_objs_per_bb=2)
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
    # rays = (rays[0][39737:39739], rays[1][39737:39739])

    start = time.time()
    res = hit3(rays, group_bbs, group_child_indexes, group_child_types, triangles_data)
    return res


if __name__ == "__main__":
    vertices, triangles = parse_obj('../obj/bunny.obj')
    vertices = vertices * 20
    #
    triangles1 = [Triangle(vertices[triangle]) for triangle in triangles]

    width = 1000
    height = 1000
    camera = Camera(width=width, height=height,
                    position=np.array([0,2,3]), yaw=0, pitch=0)
    res = render(triangles1, camera)
    res = ((res.reshape(height, width))[::-1, :] - res.min())/(res.max() - res.min())
    pass