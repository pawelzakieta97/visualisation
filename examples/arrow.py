import numpy as np

from models.coords import Coords, CoordsMesh, Arrow
from models.primitives.cone import Cone
from visualisation.meshViewer import MeshViewWindow
from visualisation.shaders.vc_shader import VertexColorShader

if __name__ == "__main__":
    win = MeshViewWindow(add_floorgrid=True, orthographic=False, target_fps=60)
    arrow = Arrow()
    win.add_object(arrow)
    def tick():
        arrow.set(end=np.cos(win.frame_number/100) * np.array([1, 1, 1]))

    win.run(tick)