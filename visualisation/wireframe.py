import numpy as np
from OpenGL.GL import *  # pylint: disable=W0614

from models.wireframe import Wireframe as WireframeModel
from visualisation.renderable import Renderable
from visualisation.shader import Shader


class Wireframe(Renderable):

    def __init__(self, model: WireframeModel):
        super().__init__()
        self.shader = None
        self.vertex_buffer = None
        self.color_buffer = None
        self.model = model

    def load_shader(self):
        self.shader = Shader()
        self.shader.initShaderFromGLSL([f"{self.SHADER_DIRECTORY}/lines/vertex_vc.glsl"],
                                       [f"{self.SHADER_DIRECTORY}/lines/fragment_vc.glsl"])
        self.MVP_ID = glGetUniformLocation(self.shader.program, "MVP")

    def load_vbos(self):
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vertex_buffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.model.lines.astype(np.float32).flatten(),
                     GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.color_buffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.model.colors.astype(np.float32).flatten(),
                     GL_STATIC_DRAW)


    def load_object(self):

        # print len(self.lines)
        self.vertex_buffer = glGenBuffers(1)
        self.color_buffer = glGenBuffers(1)
        self.load_vbos()

    def render(self, projection_matrix, view_matrix, camera_position, lights):
        if self.model.changed:
            self.load_vbos()
            self.model.changed = False
        self.shader.begin()
        glUniformMatrix4fv(self.MVP_ID, 1, GL_FALSE, (projection_matrix @ np.linalg.inv(view_matrix)).T)#glm.value_ptr(VP))

        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.color_buffer)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)

        glDrawArrays(GL_LINES, 0, len(self.model.lines.flatten()) // 3)  # 12*3 indices starting at 0 -> 12 triangles

        glDisableVertexAttribArray(0)
        self.shader.end()
