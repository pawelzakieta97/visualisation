import numpy as np
from OpenGL.GL import *  # pylint: disable=W0614

from visualisation.light import Light
from visualisation.renderable import Renderable
from visualisation.shader import Shader


class Texture(Renderable):
    def __init__(self, image_data):
        super().__init__()
        self.texture_id = glGenTextures(1)
        self.image_data = image_data
        self.shader = None
        self.indices_buffer = None
        self.normal_buffer = None
        self.vertex_buffer = None
        self.uv_buffer = None
        self.light_color_id = None
        self.light_pos_id = None
        self.object_glossiness_id = None
        self.object_reflectiveness_id = None
        self.object_diffuse_id = None
        self.camera_pos_id = None
        self.MVP_ID = None
        self.object_transformation_id = None
        self.camera_transformation_id = None
        self.shader = None

    def load_shader(self):
        self.shader = Shader()
        self.shader.initShaderFromGLSL(
            [f"{self.SHADER_DIRECTORY}/phong/vertex_textured.glsl"],
            [f"{self.SHADER_DIRECTORY}/phong/fragment_textured.glsl"])
        self.MVP_ID = glGetUniformLocation(self.shader.program, "MVP")
        self.camera_transformation_id = glGetUniformLocation(self.shader.program, "cameraTransformation")
        self.camera_pos_id = glGetUniformLocation(self.shader.program, "cameraPosition")
        self.object_diffuse_id = glGetUniformLocation(self.shader.program, "objectDiffuse")
        self.object_reflectiveness_id = glGetUniformLocation(self.shader.program, "objectReflectiveness")
        self.object_glossiness_id = glGetUniformLocation(self.shader.program, "objectGlossiness")
        self.object_transformation_id = glGetUniformLocation(self.shader.program, "objectTransformation")
        self.light_pos_id = glGetUniformLocation(self.shader.program, "lightPosition")
        self.light_color_id = glGetUniformLocation(self.shader.program, "lightColor")

    def load_object(self):
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.image_data.width, self.image_data.height , 0, GL_RGB,
                     GL_UNSIGNED_BYTE, self.image_data)

    def render(self, projection_matrix, view_matrix, camera_position, light):

        if light is None or not light:
            light = Light(position=np.array([-5, 10, -7]), color=np.array([1, 1, 1]))
        if self.mesh.changed:
            self.load_vbos()
            self.mesh.changed = False
        self.shader.begin()
        glUniformMatrix4fv(self.MVP_ID, 1, GL_FALSE, (projection_matrix @ np.linalg.inv(view_matrix)).T)

        # camera_position = np.array(camera_position)
        glUniform3fv(self.camera_pos_id, 1, camera_position)
        glUniform3fv(self.object_diffuse_id, 1, self.material.diffuse)
        glUniform3fv(self.object_reflectiveness_id, 1, self.material.reflectiveness)
        glUniform1fv(self.object_glossiness_id, 1, self.material.glossiness)
        glUniform3fv(self.light_pos_id, 1, light.position)
        glUniform3fv(self.light_color_id, 1, light.color)
        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        if self.color_buffer is not None:
            glEnableVertexAttribArray(1)
            glBindBuffer(GL_ARRAY_BUFFER, self.color_buffer)
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)

        glEnableVertexAttribArray(2)
        glBindBuffer(GL_ARRAY_BUFFER, self.normal_buffer)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, None)
        glUniformMatrix4fv(self.object_transformation_id, 1, GL_FALSE,
                           self.mesh.transformation.T)

        # glDrawArrays(GL_TRIANGLES, 0, self.vertexLen)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.indices_buffer)
        glDrawElements(
            GL_TRIANGLES,  # mode
            len(self.mesh.triangle_indices) * 3,  # // count
            GL_UNSIGNED_SHORT,  # // type
            None  # // element array buffer offset
        )

        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)
        glDisableVertexAttribArray(2)
        self.shader.end()
