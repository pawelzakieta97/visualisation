
from models.parse_obj import parse_obj
from raytracing.bvh import get_object_tree_greedy

from raytracing.renderer import render
from raytracing.triangle import Triangle

if __name__ == '__main__':

    vertices, triangles = parse_obj('../obj/bunny.obj')
    triangles = [Triangle(vertices[triangle]) for triangle in triangles]
    bvh = get_object_tree_greedy(triangles[:100], max_objs_per_bb=2, max_depth=9999999999)
    res = bvh.serialize()

    pass
