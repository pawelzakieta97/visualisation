import numpy as np
from OpenGL.GL import *  # pylint: disable=W0614

from models.wireframe import Wireframe
from visualisation.shader import Shader


class FloorGrid(Wireframe):

    def __init__(self, line_count: int = 21, line_spacing: float = 1):
        line_min = (line_count - 1)/2 * line_spacing
        line_max = -(line_count - 1)/2 * line_spacing
        ls = np.linspace(line_min, line_max, line_count)
        lines_x = np.zeros((line_count, 2, 3))
        lines_x[:, 0, 0] = line_min
        lines_x[:, 1, 0] = line_max
        lines_x[:, :, 2] = ls[:, None]

        lines_y = np.zeros((line_count, 2, 3))
        lines_y[:, 0, 2] = line_min
        lines_y[:, 1, 2] = line_max
        lines_y[:, :, 0] = ls[:, None]

        lines = np.vstack((lines_x, lines_y)).reshape(-1, 3)
        colors = np.ones_like(lines) * 0.2
        colors[line_count-1: line_count+1, 0] = 1
        colors[3*line_count-1: 3*line_count+1, 1] = 1
        super().__init__(lines=lines, colors=colors)
    #
    # def load_shader(self):
    #     self.shader = Shader()
    #     self.shader.initShaderFromGLSL([f"{self.SHADER_DIRECTORY}/flat/vertex.glsl"],
    #                                    [f"{self.SHADER_DIRECTORY}/flat/fragment.glsl"])
    #     self.MVP_ID = glGetUniformLocation(self.shader.program, "MVP")
    #
    # def load_object(self):
    #
    #
    #     # print len(self.flat)
    #     self.linebuffer = glGenBuffers(1)
    #     glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.linebuffer)
    #     glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(self.flat) * 4, (GLfloat * len(self.flat))(*self.flat),
    #                  GL_STATIC_DRAW)
    #     self.colorbuffer = glGenBuffers(1)
    #     glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.colorbuffer)
    #     glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(self.colors) * 4, (GLfloat * len(self.colors))(*self.colors),
    #                  GL_STATIC_DRAW)
    #
    # def render(self, VP, *args, **kwargs):
    #     self.shader.begin()
    #     glUniformMatrix4fv(self.MVP_ID, 1, GL_FALSE, VP.T)#glm.value_ptr(VP))
    #
    #     glEnableVertexAttribArray(0)
    #     glBindBuffer(GL_ARRAY_BUFFER, self.linebuffer)
    #     glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    #
    #     glEnableVertexAttribArray(1)
    #     glBindBuffer(GL_ARRAY_BUFFER, self.colorbuffer)
    #     glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
    #
    #     glDrawArrays(GL_LINES, 0, len(self.flat) // 3)  # 12*3 indices starting at 0 -> 12 triangles
    #
    #     glDisableVertexAttribArray(0)
    #     self.shader.end()
