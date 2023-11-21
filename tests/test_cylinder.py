from models.primitives.cylinder import Cylinder
from visualisation.meshViewer import MeshViewWindow

if __name__ == "__main__":
    cylinder = Cylinder()
    win = MeshViewWindow(add_floorgrid=True, orthographic=False, target_fps=30)
    win.add_object(cylinder)
    win.run()
