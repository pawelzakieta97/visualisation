import numpy as np
from OpenGL.GL import *  # pylint: disable=W0614

from models.mesh import Mesh
from visualisation.light import Light
from visualisation.material import Texture, Material
from visualisation.renderable import Renderable
from visualisation.shader import Shader
from visualisation.visobject import VisObject


class Map(VisObject):
    def __init__(self, data: np.array, auto_reload=True):
        mesh = Mesh(vertices=np.array([[-1, -1, 0],
                                       [1, -1, 0],
                                       [1, 1, 0],
                                       [-1, 1, 0]]),
                    triangle_indices=np.array([[0, 1, 2], [2, 3, 0]]),
                    uv=np.array([[0, 0],
                                 [1, 0],
                                 [1, 1],
                                 [0, 1]]))
        super().__init__(mesh, material=Material(diffuse=data, texture_interpolation=GL_NEAREST))
        self.auto_reload = auto_reload
    #
    # def render(self, projection_view_matrix, camera_position, light):
    #     self.shader.begin()
    #     glUniformMatrix4fv(self.MVP_ID, 1, GL_FALSE, projection_view_matrix.T)
    #
    #     glUniformMatrix4fv(self.object_transformation_id, 1, GL_FALSE,
    #                        self.mesh.transformation.T)
    #
    #     glEnableVertexAttribArray(0)
    #     glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
    #     glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    #
    #     glEnableVertexAttribArray(1)
    #     glBindBuffer(GL_ARRAY_BUFFER, self.uv_buffer)
    #     glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)
    #     glActiveTexture(GL_TEXTURE0)
    #     glBindTexture(GL_TEXTURE_2D, self.material.diffuse.texture_id)
    #     glUniform1i(self.TextureID, 0)
    #     # glUniform1i(self.context.TextureID, 0)
    #
    #     glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.indices_buffer)
    #     glDrawElements(
    #         GL_TRIANGLES,  # mode
    #         len(self.mesh.triangle_indices) * 3,  # // count
    #         # TODO: check bigger type
    #         GL_UNSIGNED_SHORT,  # // type
    #         None  # // element array buffer offset
    #     )
    #
    #     glDisableVertexAttribArray(0)
    #     glDisableVertexAttribArray(1)
    #     glDisableVertexAttribArray(2)
    #     self.shader.end()
    #
    # def load_shader(self):
    #     self.shader = Shader()
    #     self.shader.initShaderFromGLSL(
    #         [f"{self.SHADER_DIRECTORY}/flat/vertex_textured.glsl"],
    #         [f"{self.SHADER_DIRECTORY}/flat/fragment_textured.glsl"])
    #     self.MVP_ID = glGetUniformLocation(self.shader.program, "MVP")
    #     self.camera_transformation_id = glGetUniformLocation(self.shader.program, "cameraTransformation")
    #     self.object_transformation_id = glGetUniformLocation(self.shader.program, "objectTransformation")
    #     self.camera_pos_id = glGetUniformLocation(self.shader.program, "cameraPosition")
    #     self.TextureID = glGetUniformLocation(self.shader.program, "myTextureSampler")

    def load_vbos(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
        glBufferData(GL_ARRAY_BUFFER, self.mesh.vertices.astype(np.float32), GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, self.uv_buffer)
        glBufferData(GL_ARRAY_BUFFER, self.mesh.uv.astype(np.float32), GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, self.normal_buffer)
        glBufferData(GL_ARRAY_BUFFER, self.mesh.normals.astype(np.float32), GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.indices_buffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.mesh.triangle_indices.astype(np.uint32), GL_STATIC_DRAW)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    def update(self, data: np.ndarray, *args, **kwargs):
        self.material.diffuse = Texture(data, texture_interpolation=GL_NEAREST)
        self.material.diffuse.load()
