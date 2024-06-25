import numpy as np
import pandas as pd

from raytracing.group import Group
from raytracing.renderable import Renderable
from sphere import Sphere
# import plotly.express as px


np.random.seed(0)


def get_object_tree_greedy(meshes: list[Renderable], max_objs_per_bb=5, max_depth=10) -> Group:
    if len(meshes) <= max_objs_per_bb or max_depth<=1:
        return Group(meshes)
    bbs = np.stack([mesh.get_bb() for mesh in meshes])
    centers = bbs.mean(axis=1)
    min_cost = np.inf
    split = None
    for axis in range(3):
        sorted_idxs = np.argsort(centers[:, axis])
        for i in range(1, len(sorted_idxs)):
            left_bbs = bbs[sorted_idxs[:i]]
            right_bbs = bbs[sorted_idxs[i:]]
            left_bb_min = left_bbs[:, 0, :].min(axis=0)
            left_bb_max = left_bbs[:, 1, :].max(axis=0)
            left_bb_size = left_bb_max - left_bb_min
            left_surface = 2 * (left_bb_size[0] * left_bb_size[1] +
                                left_bb_size[1] * left_bb_size[2] +
                                left_bb_size[0] * left_bb_size[2])

            right_bb_min = right_bbs[:, 0, :].min(axis=0)
            right_bb_max = right_bbs[:, 1, :].max(axis=0)
            right_bb_size = right_bb_max - right_bb_min
            right_surface = 2 * (right_bb_size[0] * right_bb_size[1] +
                                 right_bb_size[1] * right_bb_size[2] +
                                 right_bb_size[0] * right_bb_size[2])
            total_cost = left_surface * i + right_surface * (len(sorted_idxs) - i)
            if total_cost < min_cost:
                min_cost = total_cost
                split = [sorted_idxs[:i], sorted_idxs[i:]]
    groups = [get_object_tree_greedy([meshes[s] for s in split[0]], max_objs_per_bb=max_objs_per_bb, max_depth=max_depth-1),
              get_object_tree_greedy([meshes[s] for s in split[1]], max_objs_per_bb=max_objs_per_bb, max_depth=max_depth-1)]
    return Group(groups)


def vis_group(group: Group):
    elements = group.get_elements()
    df = pd.DataFrame({'x': [e.pos[0] for e in elements], 'y': [e.pos[1] for e in elements]})
    fig = px.scatter(df, x='x', y='y')
    elements = [group]
    level = 0
    while elements:
        new_elements = []
        for element in elements:
            if not isinstance(element, Group):
                continue
            bb = element.get_bb()
            fig.add_shape(type="rect",
                          x0=bb[0, 0], y0=bb[0, 1], x1=bb[1, 0], y1=bb[1, 1],
                          line=dict(color="RoyalBlue"),
                          )
            new_elements += element.elements
        elements = new_elements
        level += 1
    fig.show()


if __name__ == '__main__':
    sphere_count = 100
    sphere_positions = np.random.random((sphere_count, 3))
    sphere_radius = np.random.random(sphere_count) * 0.05
    sphere_positions[:, 2] = sphere_radius * 0
    spheres = [Sphere(pos, r) for pos, r in zip(sphere_positions, sphere_radius)]

    tree = get_object_tree_greedy(spheres)

    vis_group(tree)

    res = tree.serialize()
    df = pd.DataFrame({'x': sphere_positions[:, 0], 'y': sphere_positions[:, 1]})
    fig = px.scatter(df, x='x', y='y')
    fig.show()

    pass
