from models.coords import Coords, CoordsMesh
from models.primitives.cone import Cone
from visualisation.meshViewer import MeshViewWindow
from visualisation.shaders.vc_shader import VertexColorShader

if __name__ == "__main__":
    win = MeshViewWindow(add_floorgrid=True, orthographic=False, target_fps=60)
    coords = CoordsMesh()
    win.add_object(coords, shader_cls=VertexColorShader)
    win.run()