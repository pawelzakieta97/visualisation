import numpy as np
from OpenGL.GL import *  # pylint: disable=W0614

from transformations import get_translation_matrix
from visualisation.light import Light
from visualisation.material import Material
from visualisation.renderable import Renderable
from visualisation.shader import Shader


from models.mesh import Mesh


class VisObject(Renderable):

    def __init__(self, mesh: Mesh, material: Material = None, shader_name='phong'):
        if material is None:
            material = Material()
        super().__init__(material=material)
        self.indices_buffer = None
        self.normal_buffer = None
        self.vertex_buffer = None
        self.color_buffer = None
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
        self.shader_name = shader_name
        self.mesh = mesh
        self.material = material

    def load_shader(self):
        self.shader = Shader()
        if self.mesh.color is None:
            self.shader.initShaderFromGLSL(
                [f"{self.SHADER_DIRECTORY}/{self.shader_name}/vertex.glsl"],
                [f"{self.SHADER_DIRECTORY}/{self.shader_name}/fragment.glsl"])
        else:
            self.shader.initShaderFromGLSL(
                [f"{self.SHADER_DIRECTORY}/{self.shader_name}/vertex_vc.glsl"],
                [f"{self.SHADER_DIRECTORY}/{self.shader_name}/fragment_vc.glsl"])
        self.MVP_ID = glGetUniformLocation(self.shader.program, "MVP")
        self.camera_transformation_id = glGetUniformLocation(self.shader.program, "cameraTransformation")
        self.camera_pos_id = glGetUniformLocation(self.shader.program, "cameraPosition")
        self.object_diffuse_id = glGetUniformLocation(self.shader.program, "objectDiffuse")
        self.object_reflectiveness_id = glGetUniformLocation(self.shader.program, "objectReflectiveness")
        self.object_glossiness_id = glGetUniformLocation(self.shader.program, "objectGlossiness")
        self.object_transformation_id = glGetUniformLocation(self.shader.program, "objectTransformation")
        self.light_pos_id = glGetUniformLocation(self.shader.program, "lightPosition")
        self.light_color_id = glGetUniformLocation(self.shader.program, "lightColor")

    def load_vbos(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
        glBufferData(GL_ARRAY_BUFFER, self.mesh.vertices.astype(np.float32), GL_STATIC_DRAW)

        if self.mesh.color is not None:
            glBindBuffer(GL_ARRAY_BUFFER, self.color_buffer)
            glBufferData(GL_ARRAY_BUFFER, self.mesh.color.astype(np.float32), GL_STATIC_DRAW)
        else:
            self.color_buffer = None

        glBindBuffer(GL_ARRAY_BUFFER, self.normal_buffer)
        glBufferData(GL_ARRAY_BUFFER, self.mesh.normals.astype(np.float32), GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.indices_buffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.mesh.triangle_indices.astype(np.uint16), GL_STATIC_DRAW)

    def load_object(self):
        self.vertex_buffer = glGenBuffers(1)
        self.normal_buffer = glGenBuffers(1)
        self.indices_buffer = glGenBuffers(1)
        self.color_buffer = glGenBuffers(1)
        self.load_vbos()

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
