import sys
import time

import numpy as np
import pandas as pd

from raytracing.group import Group
from raytracing.renderable import Renderable, INF_DISTANCE
from raytracing.triangle import hits_triangle, Triangle
from raytracing.sphere import hits_sphere
import numba as nb
import plotly.express as px


np.random.seed(0)


def get_object_tree_greedy(meshes: list[Renderable], max_objs_per_bb=5, max_depth=1000) -> Group:
    if len(meshes) <= max_objs_per_bb:
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
    groups = [
        get_object_tree_greedy([meshes[s] for s in split[0]], max_objs_per_bb=max_objs_per_bb, max_depth=max_depth - 1),
        get_object_tree_greedy([meshes[s] for s in split[1]], max_objs_per_bb=max_objs_per_bb, max_depth=max_depth - 1)]
    return Group(groups)


def get_object_tree_fast(meshes: list[Renderable], max_objs_per_bb=5, max_depth=1000) -> Group:
    """
    TODO: optimizations:    numba implementation (large amount of time is spent on deep nodes with few children
                            generate bbs once instead of in every function call
    """
    if len(meshes) <= max_objs_per_bb:
        return Group(meshes)
    bbs = np.stack([mesh.get_bb() for mesh in meshes])
    centers = bbs.mean(axis=1)
    min_cost = np.inf
    split = None
    for axis in range(3):
        sorted_idxs = np.argsort(centers[:, axis])
        left_bb_mins = np.minimum.accumulate(bbs[sorted_idxs][:, 0, :], axis=0)
        left_bb_maxs = np.maximum.accumulate(bbs[sorted_idxs][:, 1, :], axis=0)
        left_bb_sizes = left_bb_maxs - left_bb_mins
        left_surfaces = 2 * (left_bb_sizes[:, 0] * left_bb_sizes[:, 1] +
                             left_bb_sizes[:, 1] * left_bb_sizes[:, 2] +
                             left_bb_sizes[:, 0] * left_bb_sizes[:, 2])

        right_bb_mins = np.minimum.accumulate(bbs[sorted_idxs[::-1]][:, 0, :], axis=0)[::-1]
        right_bb_maxs = np.maximum.accumulate(bbs[sorted_idxs[::-1]][:, 1, :], axis=0)[::-1]
        right_bb_sizes = right_bb_maxs - right_bb_mins
        right_surfaces = 2 * (right_bb_sizes[:, 0] * right_bb_sizes[:, 1] +
                              right_bb_sizes[:, 1] * right_bb_sizes[:, 2] +
                              right_bb_sizes[:, 0] * right_bb_sizes[:, 2])

        # object counts are off by one - this way the first object is "free" which forces the algorithm to always
        # split objects to separate groups until reaching minimum objects per bb
        left_object_counts = np.arange(len(meshes))
        right_object_counts = np.arange(len(meshes)-1, -1, -1)
        total_costs = left_surfaces * left_object_counts + right_surfaces * right_object_counts
        split_idx = total_costs.argmin()
        if total_costs[split_idx] < min_cost:
            split = [sorted_idxs[:split_idx+1], sorted_idxs[split_idx+1:]]
            min_cost = total_costs[split_idx]
    groups = [
        get_object_tree_fast([meshes[s] for s in split[0]], max_objs_per_bb=max_objs_per_bb, max_depth=max_depth - 1),
        get_object_tree_fast([meshes[s] for s in split[1]], max_objs_per_bb=max_objs_per_bb, max_depth=max_depth - 1)]
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


def hits_box(ray_starts, ray_directions, bbs, return_distances=False):
    bbs_min = bbs[:, 0, :]
    bbs_max = bbs[:, 1, :]
    t_min = (bbs_min - ray_starts) / ray_directions
    t_max = (bbs_max - ray_starts) / ray_directions
    # negative t means that the ray will not intersect the plane.
    # Setting to large number will make result in failed boundary check
    t_min[t_min < 0] = INF_DISTANCE
    t_max[t_max < 0] = INF_DISTANCE
    t = t_min
    mask = t_max < t_min
    t[mask] = t_max[mask]
    # t = t[:, :2]
    hit_points = ray_starts[:, None, :] + ray_directions[:, None, :] * t[:, :, None]

    margin = 0.0001
    hits = (bbs_min[:, None, :] <= hit_points + margin) & (hit_points <= bbs_max[:, None, :] + margin)

    # hits within limits in all dimensions
    hits_within_limits = hits.all(axis=-1)
    hits_any_wall = hits_within_limits.any(axis=-1)
    if return_distances:
        distances = t * hits_within_limits
        distances[distances == 0] = INF_DISTANCE
        # distances[~hits_any_wall] = INF_DISTANCE
        return hits_any_wall, distances.min(axis=-1)
    return hits_any_wall


def hit_triangle_bvh(rays, bbs, group_child_indexes, children_types, triangles_data):
    """
    Vectorized bounding volume hierarchy traversing, handling triangles
    """
    ray_starts = rays[0]
    ray_count = ray_starts.shape[0]
    ray_directions = rays[1]
    depth = 128


    _ray_starts = ray_starts.copy()
    _ray_directions = ray_directions.copy()
    # candidates - objects that are hit and should be explored
    candidates = np.zeros((ray_count, depth)).astype(int)
    candidate_lengths = np.ones(ray_count).astype(int)
    min_hit_distances = np.ones(ray_count) * INF_DISTANCE

    ray_indexes = np.arange(ray_count)

    ray_hit_ids = np.ones(ray_count, dtype=int) * -1
    ray_hit_distances = np.ones(ray_count) * INF_DISTANCE

    triangles_h = triangles_data[:, 15]
    triangles_normals = triangles_data[:, 12:15]
    triangles_Ts = triangles_data[:, :12].reshape(-1, 3, 4)
    group_history = []
    search_depth = np.zeros(ray_starts.shape[0])
    for i in range(20000):
        # id of elements to be checked (both groups and primitives)
        explored_ids = candidates[np.arange(candidates.shape[0]), candidate_lengths-1]
        group_history.append(explored_ids)
        checked_children_ids = group_child_indexes[explored_ids, :]
        checked_children_types = children_types[explored_ids, :]
        checked_children_triangle_mask = (checked_children_types == Triangle.get_type_id())[:, 0]
        # ray_hit_ids[ray_indexes[checked_children_triangle_mask]] = i
        checked_children_triangle_indexes = np.where(checked_children_triangle_mask)[0]
        checked_children_triangle_ids = checked_children_ids[checked_children_triangle_mask, :]
        checked_children_triangle_ids_0 = checked_children_triangle_ids[:, 0]
        checked_children_triangle_ids_1 = checked_children_triangle_ids[:, 1]
        if (checked_children_triangle_ids_0).any():
            search_depth[ray_indexes] += 1
            pass
        triangle_0_distances = hits_triangle(ray_starts[checked_children_triangle_mask],
                                         ray_directions[checked_children_triangle_mask],
                                         triangles_Ts[checked_children_triangle_ids_0, :, :],
                                         triangles_normals[checked_children_triangle_ids_0, :],
                                         triangles_h[checked_children_triangle_ids_0])
        multi_element_group_mask = checked_children_triangle_ids_1 != -1
        multi_element_group_indexes = np.where(multi_element_group_mask)[0]
        triangle_1_distances = hits_triangle(ray_starts[checked_children_triangle_indexes[multi_element_group_mask]],
                                         ray_directions[checked_children_triangle_indexes[multi_element_group_mask]],
                                         triangles_Ts[checked_children_triangle_ids_1[multi_element_group_mask], :, :],
                                         triangles_normals[checked_children_triangle_ids_1[multi_element_group_mask], :],
                                         triangles_h[checked_children_triangle_ids_1[multi_element_group_mask]])
        triangle_0_closer = triangle_0_distances < min_hit_distances[checked_children_triangle_indexes]
        min_hit_distances[checked_children_triangle_indexes[triangle_0_closer]] = triangle_0_distances[triangle_0_closer]
        ray_hit_ids[ray_indexes[checked_children_triangle_indexes[triangle_0_closer]]] = checked_children_triangle_ids_0[triangle_0_closer]

        triangle_1_closer = triangle_1_distances < min_hit_distances[checked_children_triangle_indexes[multi_element_group_mask]]
        min_hit_distances[checked_children_triangle_indexes[multi_element_group_indexes[triangle_1_closer]]] = triangle_1_distances[triangle_1_closer]
        ray_hit_ids[ray_indexes[checked_children_triangle_indexes[multi_element_group_indexes[triangle_1_closer]]]] = (
            checked_children_triangle_ids_1)[multi_element_group_indexes[triangle_1_closer]]


        checked_children_groups_mask = (checked_children_types == Group.get_type_id())[:, 0]
        checked_children_groups_indexes = np.where(checked_children_groups_mask)[0]
        checked_children_group_ids = checked_children_ids[checked_children_groups_mask, :]
        checked_children_group_ids_0 = checked_children_group_ids[:, 0]
        checked_children_group_ids_1 = checked_children_group_ids[:, 1]

        group_0_hits, group_0_distances = hits_box(ray_starts[checked_children_groups_mask, :],
                                                   ray_directions[checked_children_groups_mask, :],
                                                   bbs[checked_children_group_ids_0, :, :],
                                                   return_distances=True)
        # group_0_hits[:] = 1
        # group_0_distances[:] = 0
        group_1_hits, group_1_distances = hits_box(ray_starts[checked_children_groups_mask, :],
                                                   ray_directions[checked_children_groups_mask, :],
                                                   bbs[checked_children_group_ids_1, :, :],
                                                   return_distances=True)
        # group_1_hits[:] = 1
        # group_1_distances[:] = 0
        group_0_hits[group_0_distances > min_hit_distances[checked_children_groups_mask]] = 0
        group_1_hits[group_1_distances > min_hit_distances[checked_children_groups_mask]] = 0
        # BOTH GROUPS HIT
        both_groups_hit_mask = group_0_hits & group_1_hits
        both_groups_hit_indexes = np.where(both_groups_hit_mask)[0]
        group_1_closer = group_1_distances[both_groups_hit_mask] < group_0_distances[both_groups_hit_mask]
        swap_indexes = both_groups_hit_indexes[group_1_closer]
        swap_id_0 = checked_children_group_ids_0[swap_indexes]
        checked_children_group_ids_0[swap_indexes] = checked_children_group_ids_1[swap_indexes]
        checked_children_group_ids_1[swap_indexes] = swap_id_0

        candidate_lengths -= 1

        candidates[checked_children_groups_indexes[group_1_hits], candidate_lengths[checked_children_groups_indexes[group_1_hits]]] = checked_children_group_ids_1[group_1_hits]
        candidate_lengths[checked_children_groups_indexes[group_1_hits]] += 1

        candidates[checked_children_groups_indexes[group_0_hits], candidate_lengths[checked_children_groups_indexes[group_0_hits]]] = checked_children_group_ids_0[group_0_hits]
        candidate_lengths[checked_children_groups_indexes[group_0_hits]] += 1

        candidate_mask = candidate_lengths > 0
        if not candidate_mask.any():
            break
        ray_starts = ray_starts[candidate_mask, :]
        ray_directions = ray_directions[candidate_mask, :]
        ray_hit_distances[ray_indexes] = min_hit_distances
        candidates = candidates[candidate_mask, :]
        candidate_lengths = candidate_lengths[candidate_mask]
        min_hit_distances = min_hit_distances[candidate_mask]
        ray_indexes = ray_indexes[candidate_mask]
    print(i)
    hits = np.zeros(ray_count)
    hits[ray_indexes] = 1
    return ray_hit_ids, ray_hit_distances


def hit_sphere_bvh(rays, bbs, group_child_indexes, children_types, spheres_data):
    """
    Vectorized bounding volume hierarchy traversing
    """
    ray_starts = rays[0]
    ray_count = ray_starts.shape[0]
    ray_directions = rays[1]
    depth = 128

    # candidates - objects that are hit and should be explored
    candidates = np.zeros((ray_count, depth)).astype(int)
    candidate_lengths = np.ones(ray_count).astype(int)
    min_hit_distances = np.ones(ray_count) * INF_DISTANCE
    # min_hit_distances = np.random.random(ray_count) * 40

    ray_indexes = np.arange(ray_count)

    ray_hit_ids = np.ones(ray_count, dtype=int) * -1
    ray_hit_distances = np.ones(ray_count) * INF_DISTANCE
    spheres_pos = spheres_data[:, :3]
    spheres_r = spheres_data[:, 3]
    for i in range(20000):
        # id of elements to be checked (both groups and primitives)
        explored_ids = candidates[np.arange(candidates.shape[0]), candidate_lengths-1]

        checked_children_ids = group_child_indexes[explored_ids, :]
        checked_children_types = children_types[explored_ids, :]

        checked_children_sphere_mask = (checked_children_types == ENTITY_TYPE_MAP['sphere'])[:, 0]
        checked_children_sphere_indexes = np.where(checked_children_sphere_mask)[0]
        checked_children_sphere_ids = checked_children_ids[checked_children_sphere_mask, :]
        checked_children_sphere_ids_0 = checked_children_sphere_ids[:, 0]
        checked_children_sphere_ids_1 = checked_children_sphere_ids[:, 1]

        sphere_0_distances = hits_sphere(ray_starts[checked_children_sphere_mask],
                                         ray_directions[checked_children_sphere_mask],
                                         spheres_pos[checked_children_sphere_ids_0, :],
                                         spheres_r[checked_children_sphere_ids_0])
        multi_element_group_mask = checked_children_sphere_ids_1 != -1
        multi_element_group_indexes = np.where(multi_element_group_mask)[0]
        sphere_1_distances = hits_sphere(ray_starts[checked_children_sphere_indexes[multi_element_group_mask]],
                                         ray_directions[checked_children_sphere_indexes[multi_element_group_mask]],
                                         spheres_pos[checked_children_sphere_ids_1[multi_element_group_mask], :],
                                         spheres_r[checked_children_sphere_ids_1[multi_element_group_mask]])
        sphere_0_closer = sphere_0_distances < min_hit_distances[checked_children_sphere_indexes]
        min_hit_distances[checked_children_sphere_indexes[sphere_0_closer]] = sphere_0_distances[sphere_0_closer]
        ray_hit_ids[ray_indexes[checked_children_sphere_indexes[sphere_0_closer]]] = checked_children_sphere_ids_0[sphere_0_closer]

        sphere_1_closer = sphere_1_distances < min_hit_distances[checked_children_sphere_indexes[multi_element_group_mask]]
        min_hit_distances[checked_children_sphere_indexes[multi_element_group_indexes[sphere_1_closer]]] = sphere_1_distances[sphere_1_closer]
        ray_hit_ids[ray_indexes[checked_children_sphere_indexes[multi_element_group_indexes[sphere_1_closer]]]] = (
            checked_children_sphere_ids_1)[multi_element_group_indexes[sphere_1_closer]]

        checked_children_groups_mask = (checked_children_types == ENTITY_TYPE_MAP['group'])[:, 0]
        checked_children_groups_indexes = np.where(checked_children_groups_mask)[0]
        checked_children_group_ids = checked_children_ids[checked_children_groups_mask, :]
        checked_children_group_ids_0 = checked_children_group_ids[:, 0]
        checked_children_group_ids_1 = checked_children_group_ids[:, 1]

        group_0_hits, group_0_distances = hits_box(ray_starts[checked_children_groups_mask, :],
                                                   ray_directions[checked_children_groups_mask, :],
                                                   bbs[checked_children_group_ids_0, :, :],
                                                   return_distances=True)
        group_1_hits, group_1_distances = hits_box(ray_starts[checked_children_groups_mask, :],
                                                   ray_directions[checked_children_groups_mask, :],
                                                   bbs[checked_children_group_ids_1, :, :],
                                                   return_distances=True)
        group_0_hits[group_0_distances > min_hit_distances[checked_children_groups_mask]] = 0
        group_1_hits[group_1_distances > min_hit_distances[checked_children_groups_mask]] = 0
        # BOTH GROUPS HIT
        both_groups_hit_mask = group_0_hits & group_1_hits
        both_groups_hit_indexes = np.where(both_groups_hit_mask)[0]
        group_1_closer = group_1_distances[both_groups_hit_mask] < group_0_distances[both_groups_hit_mask]
        swap_indexes = both_groups_hit_indexes[group_1_closer]
        swap_id_0 = checked_children_group_ids_0[swap_indexes]
        checked_children_group_ids_0[swap_indexes] = checked_children_group_ids_1[swap_indexes]
        checked_children_group_ids_1[swap_indexes] = swap_id_0

        candidate_lengths -= 1

        candidates[checked_children_groups_indexes[group_1_hits], candidate_lengths[checked_children_groups_indexes[group_1_hits]]] = checked_children_group_ids_1[group_1_hits]
        candidate_lengths[checked_children_groups_indexes[group_1_hits]] += 1

        candidates[checked_children_groups_indexes[group_0_hits], candidate_lengths[checked_children_groups_indexes[group_0_hits]]] = checked_children_group_ids_0[group_0_hits]
        candidate_lengths[checked_children_groups_indexes[group_0_hits]] += 1

        candidate_mask = candidate_lengths > 0
        if not candidate_mask.any():
            break
        ray_starts = ray_starts[candidate_mask, :]
        ray_directions = ray_directions[candidate_mask, :]
        candidates = candidates[candidate_mask, :]
        candidate_lengths = candidate_lengths[candidate_mask]
        min_hit_distances = min_hit_distances[candidate_mask]
        ray_hit_distances[ray_indexes] = min_hit_distances
        ray_indexes = ray_indexes[candidate_mask]
    print(i)
    hits = np.zeros(ray_count)
    hits[ray_indexes] = 1
    return ray_hit_ids, ray_hit_distances