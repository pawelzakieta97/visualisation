import numpy as np

from models.coords import Coords, CoordsMesh
from models.primitives.cube import Cube
from models.primitives.cylinder import Cylinder
from transformations import rotation_matrix_to_quaternion, get_rotation_matrix_x, quaternion_multiply, \
    quaternion_to_rotation_matrix, get_rotation_matrix_z
from visualisation.meshViewer import MeshViewWindow
from visualisation.shaders.vc_shader import VertexColorShader

if __name__ == "__main__":
    win = MeshViewWindow(add_floorgrid=True, orthographic=False, target_fps=60)
    c0 = CoordsMesh()
    c1 = CoordsMesh()
    c2 = CoordsMesh()
    q = rotation_matrix_to_quaternion(c1.transformation)
    rot_mx = get_rotation_matrix_x(np.pi / 2)
    rot_qx = rotation_matrix_to_quaternion(rot_mx)
    rot_mz = get_rotation_matrix_z(np.pi / 2)
    rot_qz = rotation_matrix_to_quaternion(rot_mz)

    q = quaternion_multiply(rot_qx, q)
    # ROTATION AROUND LOCAL (OBJECT) FRAME OF REFERENCE
    q1 = quaternion_multiply(q, rot_qz)
    # ROTATION AROUND WORLD FRAME OF REFERENCE
    q2 = quaternion_multiply(rot_qz, q)
    # q = quaternion_multiply(q, rot_q)
    t = quaternion_to_rotation_matrix(q1)
    c1.transformation[:3, :3] = t
    t = quaternion_to_rotation_matrix(q2)
    c2.transformation[:3, :3] = t
    t = quaternion_to_rotation_matrix(q)
    c0.transformation[:3, :3] = t
    win.add_object(c0, shader_cls=VertexColorShader)
    c1.translate(dx=2)
    c2.translate(dx=4)
    win.add_object(c1, shader_cls=VertexColorShader)
    win.add_object(c2, shader_cls=VertexColorShader)
    win.run()
