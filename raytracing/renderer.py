from __future__ import annotations
import pickle
import time

import numpy as np
import torch

from raytracing.group import Group

from raytracing.bvh import get_object_tree_fast, hit_triangle_bvh, get_object_tree_faster, hit_triangle_bvh_torch
from raytracing.camera import Camera
from raytracing.light import SunLight, Light
from raytracing.renderable import Renderable, INF_DISTANCE
from raytracing.sky import Sky
from raytracing.triangle import Triangle
from raytracing.utils import uniform_sphere, uniform_sphere_torch

np.random.seed(2)


def render(objects: list[Renderable], camera: Camera, bounces=5, sky=None,
           lights: list[Light] = None):
    if lights is None:
        lights = [SunLight()]
    start = time.time()
    bvh = get_object_tree_faster(objects, max_objs_per_bb=2)
    print('BVH generated')
    print(time.time() - start)
    pickle.dump(bvh, open("bvh.p", "wb"))
    if sky is None:
        sky = Sky()

    def _get_max_depth(bvh: Group, start=0) -> int:
        if not isinstance(bvh, Group):
            return start
        return max([_get_max_depth(child, start + 1) for child in bvh.elements])

    def _get_group_count(bvh: Group) -> int:
        if not isinstance(bvh, Group):
            return 0
        return sum([_get_group_count(child) for child in bvh.elements]) + 1

    print(_get_max_depth(bvh))
    print(_get_group_count(bvh))
    # bvh = bvh.elements[0]
    group_child_types, group_child_indexes, group_bbs, children_data = bvh.serialize()
    group_bbs = np.array(group_bbs)
    triangles_data = np.array(children_data[Triangle.get_type_id()])
    triangle_normals = triangles_data[:, 12:15]

    # mock material properties
    diffuses = np.ones_like(triangle_normals) * 0.5

    group_child_types = np.array(group_child_types)
    group_child_indexes = np.array(group_child_indexes)
    rays = camera.get_rays()
    ray_starts = rays[0]
    ray_directions = rays[1]
    ray_colors = np.ones_like(ray_starts)
    image_color = np.zeros_like(ray_starts)
    img = np.zeros((camera.height * camera.width, 3), dtype=float)
    ray_indexes = np.arange(ray_starts.shape[0], dtype=int)
    for bounce in range(bounces):
        hit_ids, ray_hit_distances = hit_triangle_bvh((ray_starts[ray_indexes],
                                                       ray_directions[ray_indexes]), group_bbs, group_child_indexes,
                                                      group_child_types, triangles_data)
        hit_mask = hit_ids != -1

        # handle environment hits
        image_color[ray_indexes[~hit_mask], :] += ray_colors[ray_indexes[~hit_mask], :] * sky.get_color(
            ray_starts[ray_indexes[~hit_mask], :],
            ray_directions[ray_indexes[~hit_mask], :])
        # ray_colors[ray_indexes[~hit_mask], :] *= sky.get_color(ray_starts[ray_indexes[~hit_mask], :],
        #                                                        ray_directions[ray_indexes[~hit_mask], :])

        # handle geometry hits
        ray_indexes = ray_indexes[hit_mask]
        hit_ids = hit_ids[hit_mask]
        ray_hit_distances = ray_hit_distances[hit_mask]
        hit_points = ray_starts[ray_indexes, :] + ray_directions[ray_indexes, :] * ray_hit_distances[:, None]
        hit_normals = triangle_normals[hit_ids, :]
        hit_diffuses = diffuses[hit_ids, :]
        scatter_directions = hit_normals + uniform_sphere(hit_normals.shape[0])
        scatter_directions /= np.linalg.norm(scatter_directions, axis=1)[:, None]
        ray_starts[ray_indexes] = hit_points
        ray_directions[ray_indexes] = scatter_directions
        ray_colors[ray_indexes] *= hit_diffuses

        # explicit samples towards light sources
        for light in lights:
            p2l = light.get_light_direction(hit_points)
            obstacle_id, obstacle_distances = hit_triangle_bvh((ray_starts[ray_indexes], p2l), group_bbs,
                                                               group_child_indexes, group_child_types,
                                                               triangles_data)
            # TODO: change to light.get_distance()
            light_visible = obstacle_distances == INF_DISTANCE
            image_color[ray_indexes[light_visible]] += ray_colors[ray_indexes[light_visible]] * (p2l * hit_normals)[
                                                                                                    light_visible].sum(
                axis=1)[:, None] * light.color[None, :]

    img = image_color.reshape(camera.height, camera.width, 3)[::-1, :, ::-1]
    return img


def render_torch(objects: list[Renderable], camera: Camera, samples=1, bounces=5, sky=None,
                 lights: list[Light] = None, device='cpu'):
    if lights is None:
        lights = [SunLight()]
    start = time.time()
    bvh = get_object_tree_faster(objects, max_objs_per_bb=2)
    print('BVH generated')
    print(time.time() - start)
    pickle.dump(bvh, open("bvh.p", "wb"))
    if sky is None:
        sky = Sky()

    def _get_max_depth(bvh: Group, start=0) -> int:
        if not isinstance(bvh, Group):
            return start
        return max([_get_max_depth(child, start + 1) for child in bvh.elements])

    def _get_group_count(bvh: Group) -> int:
        if not isinstance(bvh, Group):
            return 0
        return sum([_get_group_count(child) for child in bvh.elements]) + 1

    print(_get_max_depth(bvh))
    print(_get_group_count(bvh))
    # bvh = bvh.elements[0]
    group_child_types, group_child_indexes, group_bbs, children_data = bvh.serialize()
    group_bbs = torch.Tensor(group_bbs).to(device)
    triangles_data = torch.Tensor(children_data[Triangle.get_type_id()]).to(device)
    triangle_normals = triangles_data[:, 12:15]

    # mock material properties
    diffuses = torch.ones_like(triangle_normals) * 0.5

    group_child_types = torch.Tensor(group_child_types).to(device, dtype=torch.uint8)
    group_child_indexes = torch.Tensor(group_child_indexes).to(device, dtype=torch.int32)
    image_color = None
    compiled = torch.compile(hit_triangle_bvh_torch)
    for sample in range(samples):
        rays = camera.get_rays()
        ray_starts = torch.Tensor(rays[0]).to(device)
        ray_directions = torch.Tensor(rays[1]).to(device)
        ray_colors = torch.ones_like(ray_starts).to(device)
        if image_color is None:
            image_color = torch.zeros_like(ray_starts).to(device)
        ray_indexes = torch.arange(ray_starts.shape[0], dtype=torch.int32).to(device)
        for bounce in range(bounces):
            # hit_ids, ray_hit_distances = hit_triangle_bvh_torch((ray_starts[ray_indexes],
            #                                                      ray_directions[ray_indexes]), group_bbs,
            #                                                     group_child_indexes, group_child_types, triangles_data,
            #                                                     device=device)
            hit_ids, ray_hit_distances = compiled((ray_starts[ray_indexes],
                                                                 ray_directions[ray_indexes]), group_bbs,
                                                                group_child_indexes, group_child_types, triangles_data,
                                                                device=device)
            hit_mask = hit_ids != -1

            # handle environment hits
            image_color[ray_indexes[~hit_mask], :] += ray_colors[ray_indexes[~hit_mask], :] * sky.get_color_torch(
                ray_starts[ray_indexes[~hit_mask], :],
                ray_directions[ray_indexes[~hit_mask], :]) / samples
            # ray_colors[ray_indexes[~hit_mask], :] *= sky.get_color(ray_starts[ray_indexes[~hit_mask], :],
            #                                                        ray_directions[ray_indexes[~hit_mask], :])

            # handle geometry hits
            ray_indexes = ray_indexes[hit_mask]
            hit_ids = hit_ids[hit_mask]
            ray_hit_distances = ray_hit_distances[hit_mask]
            hit_points = ray_starts[ray_indexes, :] + ray_directions[ray_indexes, :] * ray_hit_distances[:, None]
            hit_normals = triangle_normals[hit_ids, :]
            hit_diffuses = diffuses[hit_ids, :]
            scatter_directions = hit_normals + uniform_sphere_torch(hit_normals.shape[0], device=device)
            scatter_directions /= torch.linalg.norm(scatter_directions, axis=1)[:, None]
            ray_starts[ray_indexes] = hit_points
            ray_directions[ray_indexes] = scatter_directions
            ray_colors[ray_indexes] *= hit_diffuses

            # explicit samples towards light sources
            for light in lights:
                p2l = light.get_light_direction_torch(hit_points)
                obstacle_id, obstacle_distances = hit_triangle_bvh_torch((ray_starts[ray_indexes], p2l), group_bbs,
                                                                         group_child_indexes, group_child_types,
                                                                         triangles_data,
                                                                         device=device)
                # TODO: change to light.get_distance()
                light_visible = obstacle_distances == INF_DISTANCE
                image_color[ray_indexes[light_visible]] += (ray_colors[ray_indexes[light_visible]] *
                                                            (p2l * hit_normals)[light_visible].sum(axis=1)[:, None] *
                                                            torch.Tensor(light.color[None, :]).to(device))/samples

    img = image_color.reshape(camera.height, camera.width, 3).cpu().numpy()[::-1, :, ::-1]
    return img
