import time

import numpy as np

from models.parse_obj import parse_obj
from raytracing.camera import Camera
from raytracing.renderer import render
from raytracing.triangle import Triangle
import cv2
import pickle

from transformations import get_rotation_matrix_y

if __name__ == "__main__":
    model_name = 'dragon'
    rotation = np.pi if model_name == 'dragon' else 0
    camera_pos = [0, 1, 3.5] if model_name == 'dragon' else [0, 2, 5.0]
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
    width = 300
    height = 300
    camera = Camera(width=width, height=height,
                    position=np.array(camera_pos), yaw=0, pitch=0)
    start = time.time()
    res = render(triangles1 + floor_triangles, camera)
    hdr_image = 1/(1+1/res)
    pickle.dump(res, open(f'raytrace_{model_name}.pkl', 'wb'))
    cv2.imwrite(f'raytrace_{model_name}.png', (res/res.max() * 255).astype(np.uint8))
    print(time.time() - start)
    pass