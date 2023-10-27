import numpy as np
from OpenGL.GL import *  # pylint: disable=W0614

from .renderable import Renderable
from .shader import Shader


class FloorGrid(Renderable):

    def __init__(self):
        super().__init__()
        self.MVP_ID = None
        self.shader = None
        self.colors = None
        self.linebuffer = None
        self.lines = None

    def load_shader(self):
        self.shader = Shader()
        self.shader.initShaderFromGLSL([f"{self.SHADER_DIRECTORY}/worldsheet/vertex.glsl"],
                                       [f"{self.SHADER_DIRECTORY}/worldsheet/fragment.glsl"])
        self.MVP_ID = glGetUniformLocation(self.shader.program, "MVP")

    def load_object(self):

        line_count = 21
        line_min = -int(line_count/2)
        line_max = int(line_count/2)
        ls = np.linspace(line_min, line_max, line_count)
        lines_x = np.zeros((line_count, 2, 3))
        lines_x[:, 0, 0] = line_min
        lines_x[:, 1, 0] = line_max
        lines_x[:, :, 2] = ls[:, None]

        lines_y = np.zeros((line_count, 2, 3))
        lines_y[:, 0, 2] = line_min
        lines_y[:, 1, 2] = line_max
        lines_y[:, :, 0] = ls[:, None]

        self.lines = np.concatenate((lines_x.flatten(), lines_y.flatten()))
        self.colors = np.ones_like(self.lines).reshape(-1, 3) * 0.2
        self.colors[line_count-1: line_count+1, 0] = 1
        self.colors[3*line_count-1: 3*line_count+1, 1] = 1
        self.colors = self.colors.flatten()
        # print len(self.lines)
        self.linebuffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.linebuffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(self.lines) * 4, (GLfloat * len(self.lines))(*self.lines),
                     GL_STATIC_DRAW)
        self.colorbuffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.colorbuffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(self.colors) * 4, (GLfloat * len(self.colors))(*self.colors),
                     GL_STATIC_DRAW)

    def render(self, VP, *args, **kwargs):
        self.shader.begin()
        glUniformMatrix4fv(self.MVP_ID, 1, GL_FALSE, VP.T)#glm.value_ptr(VP))

        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self.linebuffer)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.colorbuffer)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)

        glDrawArrays(GL_LINES, 0, len(self.lines) // 3)  # 12*3 indices starting at 0 -> 12 triangles

        glDisableVertexAttribArray(0)
        self.shader.end()
