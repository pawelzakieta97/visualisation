import numpy as np

from models.primitives.sphere import Sphere
from visualisation.bitmap import Bitmap
from visualisation.meshViewer import MeshViewWindow

if __name__ == "__main__":
    win = MeshViewWindow(add_floorgrid=True, orthographic=False, target_fps=60)
    bm = Bitmap(np.random.random((480, 800)))
    win.add_object(bm)
    win.run()
