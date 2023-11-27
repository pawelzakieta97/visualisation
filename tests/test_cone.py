from models.primitives.cone import Cone
from visualisation.meshViewer import MeshViewWindow

if __name__ == "__main__":
    win = MeshViewWindow(add_floorgrid=True, orthographic=False, target_fps=60)
    cone = Cone(segments=16)
    win.add_object(cone)
    win.run()
