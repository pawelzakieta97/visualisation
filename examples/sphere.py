from PIL import Image

import numpy as np

from models.primitives.sphere import Sphere
from transformations import levels
from visualisation.material import Material
from visualisation.meshViewer import MeshViewWindow

if __name__ == "__main__":
    win = MeshViewWindow(add_floorgrid=True, orthographic=False, target_fps=60)
    sphere = Sphere(smoothness=4, init_uv=True)

    plane_obj = win.add_object(sphere)
    image_data = np.array(Image.open('../resources/dirt.jpg'))
    glossiness = levels(image_data.mean(axis=2), low=0, high=1)
    plane_obj.material = Material(diffuse=image_data.astype(np.uint8)/2,
                                  reflectiveness=image_data.astype(np.uint8),
                                  glossiness=glossiness.astype(np.uint8))

    win.run()
