import numpy as np

from PIL import Image
from models.mesh import Mesh
from models.primitives.sphere import Sphere
from visualisation.map import Map
from visualisation.material import Material
from visualisation.meshViewer import MeshViewWindow

if __name__ == "__main__":
    image_data = np.array(Image.open('../resources/lena.png'))
    img = (np.random.random((100, 100, 3)) * 255).astype(np.uint8)
    map = Map(img, auto_reload=True)
    def tick():
        map.update((np.random.random((100, 100, 3)) * 255).astype(np.uint8))
    win = MeshViewWindow(add_floorgrid=False, orthographic=False, target_fps=60, tick_func=tick, enable_control=False)

    win.add_object(map)
    win.controller.pos = np.array([0, 0, 1]).astype(float)
    win.controller.fov = 90
    win.run()
