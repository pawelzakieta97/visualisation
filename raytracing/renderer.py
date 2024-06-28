import time
from enum import Enum

from PIL import Image

import numpy as np

from raytracing.group import Group
from raytracing.sphere import Sphere

from raytracing.bvh import get_object_tree_greedy
from raytracing.camera import Camera
from raytracing.renderable import Renderable

np.random.seed(2)

ENTITY_TYPE_MAP = {
    'group': 0,
    'sphere': 1
}

INF_DISTANCE = 9999999


def hit(rays, bbs, group_child_indexes, children_types, spheres_data):
    ray_starts = rays[0]
    ray_count = ray_starts.shape[0]
    ray_directions = rays[1]
    # TODO: analyze depth size impact on performance / accuracy
    depth = 32

    candidates = np.zeros((ray_count, depth)).astype(int)
    candidates_types = np.zeros((ray_count, depth)).astype(int)
    candidate_lengths = np.ones(ray_count)

    ray_indexes = np.arange(ray_count)
    ray_min_hit_distances = np.ones(ray_count) * INF_DISTANCE
    ray_hit_ids = np.ones(ray_count, dtype=int) * -1
    spheres_pos = spheres_data[:, :3]
    spheres_r = spheres_data[:, 3]
    for i in range(10000):
        # id of elements to be checked (both groups and primitives)
        checked_ids = candidates[:, 0]

        # ----------------------- HANDLE SPHERE CHECKS -----------------------
        # mask of candidates that refer to spheres
        sphere_checks = candidates_types[:, 0] == ENTITY_TYPE_MAP['sphere']
        # hit distances of spheres. If sphere is not hit, hit distance is set to INF_DISTANCE
        sphere_hit_distances = hits_sphere(ray_starts[sphere_checks],
                                           ray_directions[sphere_checks],
                                           spheres_pos[checked_ids[sphere_checks], :],
                                           spheres_r[checked_ids[sphere_checks]])
        # indexes of original rays that are checked for sphere intersections
        sphere_check_indexes = ray_indexes[sphere_checks]

        # mask of sphere checks that are closer than previous hits
        closer_hits = ray_min_hit_distances[sphere_check_indexes] > sphere_hit_distances
        ray_min_hit_distances[sphere_check_indexes[closer_hits]] = sphere_hit_distances[closer_hits]
        ray_hit_ids[sphere_check_indexes[closer_hits]] = checked_ids[sphere_checks][closer_hits]

        # ----------------------- HANDLE BB CHECKS -----------------------
        # mask of candidates that refer to groups
        box_checks = candidates_types[:, 0] == ENTITY_TYPE_MAP['group']

        # mask of all checks that hit boxes
        box_hits = np.zeros_like(checked_ids).astype(bool)
        box_hits[box_checks] = hits_box(ray_starts[box_checks],
                                        ray_directions[box_checks],
                                        bbs[checked_ids[box_checks], :, :])
        hit_group_ids = checked_ids[box_hits]

        # ----------------------- UPDATE candidates, candidate_types AND candidate_lengths BUFFERS ---------------------
        candidates[box_hits, 1:] = candidates[box_hits, :-1]
        hit_group_children = group_child_indexes[hit_group_ids, :2]
        candidates[box_hits, :2] = hit_group_children
        candidates[~box_hits, :-1] = candidates[~box_hits, 1:]

        candidates_types[box_hits, 1:] = candidates_types[box_hits, :-1]
        candidates_types[box_hits, :2] = children_types[hit_group_ids, :2]
        candidates_types[~box_hits, :-1] = candidates_types[~box_hits, 1:]

        candidate_lengths[box_hits] = candidate_lengths[box_hits] + 1
        candidate_lengths[~box_hits] = candidate_lengths[~box_hits] - 1

        # -------------- HANDLING 1-ELEMENT GROUPS -------------------
        while True:
            skip_mask = candidates[:, 0] == -1
            if not any(skip_mask):
                break
            candidates[skip_mask, :-1] = candidates[skip_mask, 1:]
            candidates_types[skip_mask, :-1] = candidates_types[skip_mask, 1:]
            candidate_lengths[skip_mask] -= 1

        candidate_mask = candidate_lengths > 0
        if not candidate_mask.any():
            break
        ray_starts = ray_starts[candidate_mask, :]
        ray_directions = ray_directions[candidate_mask, :]
        ray_indexes = ray_indexes[candidate_mask]
        candidates = candidates[candidate_mask, :]
        candidates_types = candidates_types[candidate_mask, :]
        candidate_lengths = candidate_lengths[candidate_mask]
    print(i)
    hits = np.zeros(ray_count)
    hits[ray_indexes] = 1
    return ray_hit_ids


def hit2(rays, bbs, group_child_indexes, children_types, spheres_data):
    ray_starts = rays[0]
    ray_count = ray_starts.shape[0]
    ray_directions = rays[1]
    depth = 32

    # candidates - objects that are hit and should be explored
    candidates = np.zeros((ray_count, depth)).astype(int)
    candidates_min_possible_distance = np.ones_like(candidates) * INF_DISTANCE
    candidate_lengths = np.ones(ray_count)
    min_hit_distances = np.ones(ray_count) * INF_DISTANCE
    # min_hit_distances = np.random.random(ray_count) * 40

    ray_indexes = np.arange(ray_count)

    ray_hit_ids = np.ones(ray_count, dtype=int) * -1
    spheres_pos = spheres_data[:, :3]
    spheres_r = spheres_data[:, 3]
    for i in range(200):
        # id of elements to be checked (both groups and primitives)
        explored_ids = candidates[:, 0]

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

        candidates[:, :-1] = candidates[:, 1:]
        candidate_lengths -= 1

        candidates[checked_children_groups_indexes[group_1_hits], 1:] = candidates[checked_children_groups_indexes[group_1_hits], :-1]
        candidates[checked_children_groups_indexes[group_1_hits], 0] = checked_children_group_ids_1[group_1_hits]
        candidate_lengths[checked_children_groups_indexes[group_1_hits]] += 1

        candidates[checked_children_groups_indexes[group_0_hits], 1:] = candidates[checked_children_groups_indexes[group_0_hits], :-1]
        candidates[checked_children_groups_indexes[group_0_hits], 0] = checked_children_group_ids_0[group_0_hits]
        candidate_lengths[checked_children_groups_indexes[group_0_hits]] += 1

        candidate_mask = candidate_lengths > 0
        if not candidate_mask.any():
            break
        ray_starts = ray_starts[candidate_mask, :]
        ray_directions = ray_directions[candidate_mask, :]
        ray_indexes = ray_indexes[candidate_mask]
        candidates = candidates[candidate_mask, :]
        candidate_lengths = candidate_lengths[candidate_mask]
        min_hit_distances = min_hit_distances[candidate_mask]
    print(i)
    hits = np.zeros(ray_count)
    hits[ray_indexes] = 1
    return ray_hit_ids


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


def hits_sphere(ray_starts, ray_directions, spheres_pos, spheres_r):
    if len(ray_starts) == 0:
        return spheres_r
    dp = spheres_pos - ray_starts
    a = (ray_directions * ray_directions).sum(axis=1)
    b = - 2 * (dp * ray_directions).sum(axis=1)
    c = (dp * dp).sum(axis=1) - spheres_r * spheres_r
    delta = b * b - 4 * a * c
    distances = np.ones_like(spheres_r, dtype=float) * INF_DISTANCE
    # normals = np.zeros_like(ray_starts, dtype=float)
    hits = delta > 0
    hit_distances = (-b[hits] - np.sqrt(delta[hits])) / (2 * a[hits])
    distances[hits] = hit_distances
    # normals[hits] = ray_starts[hits, :] + ray_directions[hits, :] * hit_distances[:, None]
    return distances


def render(objects: list[Renderable], camera: Camera):
    bvh = get_object_tree_greedy(objects, max_objs_per_bb=2)
    # bvh = bvh.elements[0]
    group_child_types, group_child_indexes, group_bbs, children_data = bvh.serialize()
    types_map = {
        Group: 0,
        Sphere: 1,
        -1: -1
    }
    group_bbs = np.array(group_bbs)
    group_child_types = np.array([[types_map[c] for c in child_types] for child_types in group_child_types])
    spheres_data = children_data[Sphere]
    spheres_data = np.array(spheres_data)
    group_child_indexes = np.array(group_child_indexes)
    rays = camera.get_rays()

    start = time.time()
    res = hit2(rays, group_bbs, group_child_indexes, group_child_types, spheres_data)
    print(time.time() - start)
    return res


if __name__ == "__main__":
    width = 1000
    height = 1000
    print(hits_sphere(np.array([[0, 0, 0]]), np.array([[1, 0, 0]]), np.array([[10, 0.999999, 0]]), np.array([1])))
    sphere_count = 1000
    sphere_positions = np.random.random((sphere_count, 3)) * 20
    sphere_radius = np.random.random(sphere_count) * 0.3
    sphere_positions[:, 1] = sphere_radius * 0
    spheres = [Sphere(pos, r) for pos, r in zip(sphere_positions, sphere_radius)]
    camera = Camera(width=width, height=height,
                    position=np.array([10, 1, 28]), yaw=0, pitch=-np.pi / 16)
    res = render(spheres, camera).reshape(height, width)
    res = ((res + 1) / sphere_count * 255).astype(np.uint8)[::-1, :]
    pass
