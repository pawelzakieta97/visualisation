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


def hit(rays, bbs, group_child_indexes, children_types, spheres_data):
    ray_starts = rays[0]
    ray_count = ray_starts.shape[0]
    ray_directions = rays[1]
    bbs_min = bbs[:, 0, :]
    bbs_max = bbs[:, 1, :]
    depth = 32
    candidates = np.zeros((ray_count, depth)).astype(int)
    candidates_types = np.zeros((ray_count, depth)).astype(int)
    candidate_lengths = np.ones(ray_count)
    ray_indexes = np.arange(ray_count)
    ray_min_hit_distances = np.ones(ray_count) * 99999
    spheres_pos = spheres_data[:, :3]
    spheres_r = spheres_data[:, 3]
    for i in range(100):
        checked_ids = candidates[:, 0]
        box_checks = candidates_types[:, 0] == ENTITY_TYPE_MAP['group']
        sphere_checks = candidates_types[:, 0] == ENTITY_TYPE_MAP['sphere']
        # hits = hits_box(ray_starts,
        #                 ray_directions,
        #                 bbs[checked_ids, :, :])
        _box_hits = hits_box(ray_starts[box_checks],
                            ray_directions[box_checks],
                            bbs[checked_ids[box_checks], :, :])
        sphere_hit_distances = hits_sphere(ray_starts[sphere_checks],
                                           ray_directions[sphere_checks],
                                           spheres_pos[checked_ids[sphere_checks], :],
                                           spheres_r[checked_ids[sphere_checks]])

        sphere_check_indexes = ray_indexes[sphere_checks]

        ray_min_hit_distances[sphere_check_indexes] = np.min((ray_min_hit_distances[sphere_check_indexes],
                                                              sphere_hit_distances), axis=0)
        box_hits = np.zeros_like(checked_ids).astype(bool)
        box_hits[box_checks] = _box_hits
        # hits[sphere_checks] = sphere_hit_distances < 99999
        hit_group_ids = checked_ids[box_hits]

        candidates[box_hits, 1:] = candidates[box_hits, :-1]
        candidates[box_hits, :2] = group_child_indexes[hit_group_ids, :2]
        candidates[~box_hits, :-1] = candidates[~box_hits, 1:]

        candidates_types[box_hits, 1:] = candidates_types[box_hits, :-1]
        candidates_types[box_hits, :2] = children_types[hit_group_ids, :2]
        candidates_types[~box_hits, :-1] = candidates_types[~box_hits, 1:]

        candidate_lengths[box_hits] = candidate_lengths[box_hits] + 1
        candidate_lengths[~box_hits] = candidate_lengths[~box_hits] - 1

        candidate_mask = candidate_lengths > 0
        if len(candidate_mask) == 0:
            break
        ray_starts = ray_starts[candidate_mask, :]
        ray_directions = ray_directions[candidate_mask, :]
        ray_indexes = ray_indexes[candidate_mask]
        candidates = candidates[candidate_mask, :]
        candidates_types = candidates_types[candidate_mask, :]
        candidate_lengths = candidate_lengths[candidate_mask]
    # return hits
    hits = np.zeros(ray_count)
    hits[ray_indexes] = 1
    return ray_min_hit_distances
    return hits

    pass


def hits_box(ray_starts, ray_directions, bbs):
    bbs_min = bbs[:, 0, :]
    bbs_max = bbs[:, 1, :]
    t_min = (bbs_min - ray_starts) / ray_directions
    t_max = (bbs_max - ray_starts) / ray_directions
    # negative t means that the ray will not intersect the plane.
    # Setting to large number will make result in failed boundary check
    t_min[t_min < 0] = 99999999
    t_max[t_max < 0] = 99999999
    t = t_min
    mask = t_max < t_min
    t[mask] = t_max[mask]
    # t = t[:, :2]
    hit_points = ray_starts[:, None, :] + ray_directions[:, None, :] * t[:, :, None]
    # hit_points_x_plane = hit_points[:, 0, :]
    # hit_points_y_plane = hit_points[:, 1, :]
    # hit_points_z_plane = hit_points[:, 2, :]
    margin = 0.0001
    hits = (bbs_min[:, None, :] <= hit_points + margin) & (hit_points <= bbs_max[:, None, :] + margin)
    # TODO: return distances
    return hits.all(axis=-1).any(axis=-1)


def hits_sphere(ray_starts, ray_directions, spheres_pos, spheres_r):
    dp = spheres_pos - ray_starts
    a = (ray_directions * ray_directions).sum(axis=1)
    b = - 2 * (dp * ray_directions).sum(axis=1)
    c = (dp * dp).sum(axis=1) - spheres_r * spheres_r
    delta = b * b - 4 * a * c
    distances = np.ones_like(spheres_r, dtype=float) * 99999999
    hits = delta > 0
    distances[hits] = (-b[hits] - np.sqrt(delta[hits])) / (2 * a[hits])
    return distances


def render(objects: list[Renderable], camera: Camera):
    bvh = get_object_tree_greedy(objects, max_objs_per_bb=2)
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
    # rays = (
    #     np.array([[0.5, 0.5, 10]]),
    #     np.array([[0.01, 0.01, -1]])
    # )
    test_bbs = np.stack([np.array([[0, 0, 0], [1, 1, 1]])] * len(rays[0]), axis=0)
    # return hits_box(rays[0], rays[1], test_bbs)
    res = hit(rays, group_bbs, group_child_indexes, group_child_types, spheres_data)
    return res


if __name__ == "__main__":
    print(hits_sphere(np.array([[0, 0, 0]]), np.array([[1, 0, 0]]), np.array([[10, 0.999999, 0]]), np.array([1])))
    sphere_count = 100
    sphere_positions = np.random.random((sphere_count, 3)) * 20
    sphere_radius = np.random.random(sphere_count) *2
    sphere_positions[:, 1] = sphere_radius * 0
    spheres = [Sphere(pos, r) for pos, r in zip(sphere_positions, sphere_radius)]
    res = render(spheres, Camera(position=np.array([2, -4, 20]), yaw=0)).reshape(240, 320) < 999
    pass
