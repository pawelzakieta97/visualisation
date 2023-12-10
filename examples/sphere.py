from models.primitives.sphere import Sphere
from visualisation.meshViewer import MeshViewWindow

if __name__ == "__main__":
    win = MeshViewWindow(add_floorgrid=True, orthographic=False, target_fps=60)
    sphere = Sphere()
    win.add_object(sphere)
    win.run()
