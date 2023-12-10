from models.primitives.cylinder import Cylinder
from visualisation.meshViewer import MeshViewWindow

if __name__ == "__main__":
    win = MeshViewWindow(add_floorgrid=True, orthographic=False, target_fps=60)
    cylinder = Cylinder(segments=10)
    win.add_object(cylinder)
    win.run()
