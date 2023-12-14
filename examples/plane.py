import numpy as np

from PIL import Image
from models.mesh import Mesh
from models.primitives.sphere import Sphere
from visualisation.material import Material
from visualisation.meshViewer import MeshViewWindow

if __name__ == "__main__":
    win = MeshViewWindow(add_floorgrid=True, orthographic=False, target_fps=60)
    image_data = np.array(Image.open('../resources/lena.png'))
    plane = Mesh(vertices=np.array([[0, 0, 0],
                                    [1, 0, 0],
                                    [1, 0, 1],
                                    [0, 0, 1]]),
                 triangle_indices=np.array([[0, 1, 2], [2, 3, 0]]),
                 uv=np.array([[0, 0],
                              [1, 0],
                              [1, 1],
                              [0, 1]]))
    plane = win.add_object(plane)
    plane.material = Material(diffuse=image_data.astype(np.uint8),
                              # reflectiveness=(np.random.random((10, 10, 3))*255).astype(np.uint8),
                              glossiness=image_data.mean(axis=2).astype(np.uint8),
                              # glossiness=(np.random.random((10, 10))*255).astype(np.uint8))
                              )
    win.run()