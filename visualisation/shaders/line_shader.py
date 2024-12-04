import os

import numpy as np

from visualisation.light import Light
from visualisation.material import Texture
from visualisation.shader import Shader
from visualisation.visobject import VisObject
from OpenGL.GL import *  # pylint: disable=W0614

from visualisation.wireframe import Wireframe


class LineShader(Shader):
    """
    This shader renders lines with given colors

    """
    VERTEX_PATH = "../glsl/phong/vertex_textured.glsl"
    FRAGMENT_PATH = "../glsl/phong/fragment_universal.glsl"

    def __init__(self, max_lights=10):

        super().__init__(os.path.join(self.SHADER_DIRECTORY, 'phong', 'vertex_vc.glsl'),
                         os.path.join(self.SHADER_DIRECTORY, 'phong', 'fragment_vc.glsl'),
                         priority=0)
        self.object_transformation_id = None
        self.pv_id = None
        self.camera_transformation_id = None
        self.camera_pos_id = None

    def load(self):
        super().load()
        self.pv_id = glGetUniformLocation(self.program, "projectionView")
        self.camera_transformation_id = glGetUniformLocation(self.program, "cameraTransformation")
        self.camera_pos_id = glGetUniformLocation(self.program, "cameraPosition")
        self.object_transformation_id = glGetUniformLocation(self.program, "objectTransformation")

    def render(self, objects: list[Wireframe], lights: list[Light],
               projection_view_matrix: np.array, camera_position: np.array):
        self.begin()
        glUniformMatrix4fv(self.pv_id, 1, GL_FALSE, projection_view_matrix.T)
        glUniform3fv(self.camera_pos_id, 1, camera_position)

        for wireframe in objects:
            if wireframe.model.changed:
                wireframe.load_vbos()
                wireframe.model.changed = False

            self.bind_buffers(wireframe)
            glUniformMatrix4fv(self.object_transformation_id, 1, GL_FALSE, np.eye(4).T)

            glDrawArrays(GL_LINES, 0, len(wireframe.model.lines.flatten()) // 3)

            glDisableVertexAttribArray(0)
            glDisableVertexAttribArray(1)
            glDisableVertexAttribArray(2)
            glDisableVertexAttribArray(3)
        self.end()

    def bind_buffers(self, vis_object: Wireframe):
        # binding vertex buffer
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)
        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, vis_object.vertex_buffer)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)


        glEnableVertexAttribArray(3)
        glBindBuffer(GL_ARRAY_BUFFER, vis_object.color_buffer)
        glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, 0, None)
