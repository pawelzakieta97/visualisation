import numpy as np

from PIL import Image
from models.mesh import Mesh
from models.primitives.sphere import Sphere
from transformations import levels
from visualisation.material import Material
from visualisation.meshViewer import MeshViewWindow


if __name__ == "__main__":
    win = MeshViewWindow(add_floorgrid=False, orthographic=False, target_fps=60)
    win.controller.pos = np.array([0,0.1,0])
    win.controller.pitch = -np.pi/2

    image_data = np.array(Image.open('../resources/dirt.jpg'))
    plane = Mesh(vertices=np.array([[-1, 0, -1],
                                    [-1, 0, 1],
                                    [1, 0, 1],
                                    [1, 0, -1]]) * 5,
                 triangle_indices=np.array([[0, 1, 2], [2, 3, 0]]),
                 uv=np.array([[0, 0],
                              [1, 0],
                              [1, 1],
                              [0, 1]]))
    plane = win.add_object(plane)
    glossiness = levels(image_data.mean(axis=2), low=0.1, high=1)
    diffuse = levels(image_data, high=0.5)
    reflectiveness = levels(image_data, low=0, high=0.4)
    plane.material = Material(diffuse=diffuse,
                              reflectiveness=reflectiveness,
                              glossiness=glossiness,
                              # glossiness=(np.random.random((10, 10))*255).astype(np.uint8))
                              )
    win.run()
