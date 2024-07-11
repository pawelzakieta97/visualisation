import time

import numpy as np

from models.parse_obj import parse_obj
from raytracing.camera import Camera
from raytracing.renderer import render, render_torch
from raytracing.triangle import Triangle
import cv2
import pickle

from transformations import get_rotation_matrix_y

if __name__ == "__main__":
    gpu_render = True
    model_name = 'dragon'
    samples = 10
    rotation = 1.2 * np.pi if model_name == 'dragon' else 0
    camera_pos = [-0.4, 1, 4] if model_name == 'dragon' else [0, 2, 5.0]
    vertices, triangles = parse_obj(f'../obj/{model_name}_normalized.obj')
    m = get_rotation_matrix_y(rotation)
    vertices = (m @ np.concatenate((vertices, np.ones((vertices.shape[0], 1))), axis=1).T).T[:,:3]
    print('obj loaded')
    triangles1 = [Triangle(vertices[triangle]) for triangle in triangles]
    floor_triangles = [Triangle(np.array([[-10, 0, -10],
                                          [-10, 0, 10],
                                          [10, 0, -10]])),
                       Triangle(np.array([[10, 0, -10],
                                          [-10, 0, 10],
                                          [10, 0, 10]]))
                       ]
    print('triangles processed')
    width = 2000
    height = 2000
    camera = Camera(width=width, height=height,
                    position=np.array(camera_pos), yaw=0, pitch=0)
    start = time.time()
    if not gpu_render:
        res = render(triangles1 + floor_triangles, camera)
    else:
        res = render_torch(triangles1 + floor_triangles, camera, samples=samples, device='cuda')
    hdr_image = 1/(1+1/res)
    hdr_image[hdr_image > 1] = 1
    pickle.dump(res, open(f'raytrace_{model_name}.pkl', 'wb'))
    cv2.imwrite(f'raytrace_{model_name}.png', (hdr_image * 255).astype(np.uint8))
    print(time.time() - start)
    pass