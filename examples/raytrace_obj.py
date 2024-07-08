import numpy as np

from models.parse_obj import parse_obj
from raytracing.camera import Camera
from raytracing.renderer import render
from raytracing.triangle import Triangle


if __name__ == "__main__":
    vertices, triangles = parse_obj('../obj/bunny.obj')
    print('obj loaded')
    vertices = vertices * 20
    vertices[:, 1] -= vertices[:, 1].min()
    #
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
                    position=np.array([0,1,3]), yaw=0, pitch=0)
    res = render(triangles1 + floor_triangles, camera)
    res = ((res.reshape(height, width))[::-1, :] - res.min())/(res.max() - res.min())
    pass