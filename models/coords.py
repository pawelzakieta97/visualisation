import numpy as np

from models.mesh import Mesh
from models.multi_mesh import merge_meshes
from models.primitives.cone import Cone
from models.primitives.cylinder import Cylinder
from models.wireframe import Wireframe
from transformations import get_translation_matrix, look_at, get_scale_matrix, get_rotation_matrix_x


class Coords(Wireframe):
    def __init__(self, scale=1.0):
        super().__init__(lines=np.array([[0,0,0],[0,0,1],[0,0,0],[0,1,0],[0,0,0],[1,0,0]], dtype=np.float32) * scale,
                         colors=np.array([[0,0,1],[0,0,1],[0,1,0],[0,1,0],[1,0,0],[1,0,0]], dtype=np.float32))

class Arrow(Mesh):
    def __init__(self, segments=30, start=(0,0,0), end=(0,1,0)):
        arrow_body = Cylinder(segments=segments)
        self.segments = segments
        arrow_body.scale(sx=0.02, sz=0.02)
        arrow_head = Cone()
        arrow_head.translate(dy=1)
        arrow_head.scale(sx=0.05, sy=0.1, sz=0.05)
        arrow_verts, arrow_indices, *_ = merge_meshes([arrow_body, arrow_head], as_mesh=False)
        super().__init__(arrow_verts, arrow_indices)
        self.start = start
        self.end = end
        self.set(start=start, end=end)

    def set(self, start=None, end=None):
        if start is None:
            start = self.start
        if end is None:
            end = self.end
        start = np.array(start)
        end = np.array(end)
        look_at_transformation = look_at(start, end)
        look_at_transformation @= get_rotation_matrix_x(-np.pi/2)
        self.transformation = look_at_transformation
        self.transformation @= get_scale_matrix(sy=np.linalg.norm(start-end))
        self.changed = True

class CoordsMesh(Mesh):
    def __init__(self, pos=(0, 0, 0), T=None):
        arrow_body = Cylinder()
        arrow_body.scale(sx=0.02, sz=0.02)
        arrow_head = Cone()
        arrow_head.translate(dy=1)
        arrow_head.scale(sx=0.05, sy=0.1, sz=0.05)
        arrow_y = merge_meshes([arrow_body, arrow_head], as_mesh=True)
        arrow_y.color = arrow_y.vertices * 0
        arrow_x = arrow_y.copy()
        arrow_x.rotate_z(-np.pi/2)
        arrow_z = arrow_y.copy()
        arrow_z.rotate_x(np.pi/2)
        arrow_x.color*=0.0
        arrow_x.color[:, 0] = 1.0
        arrow_y.color*=0.0
        arrow_y.color[:, 1] = 1.0
        arrow_z.color*=0.0
        arrow_z.color[:, 2] = 1.0
        arrow_verts, arrow_indices, arrow_colors, arrow_normals = merge_meshes([arrow_x, arrow_y, arrow_z])
        super().__init__(arrow_verts, arrow_indices, arrow_colors)
        t = get_translation_matrix(translation=np.array(pos))
        if T is not None:
            t = T
        self.translation = t
