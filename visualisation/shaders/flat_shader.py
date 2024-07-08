import os

import numpy as np

from visualisation.light import Light
from visualisation.material import Texture
from visualisation.shader import Shader
from visualisation.visobject import VisObject
from OpenGL.GL import *  # pylint: disable=W0614


class StandardShader(Shader):
    """
    This shader provides a standard phong rendering
    (using shadows requires that light's depth map has been already rendered)

    """
    VERTEX_PATH = "../glsl/phong/vertex_textured.glsl"
    FRAGMENT_PATH = "../glsl/phong/fragment_universal.glsl"

    def __init__(self, max_lights=10):

        super().__init__(os.path.join(self.SHADER_DIRECTORY, 'flat', 'vertex_textured.glsl'),
                         os.path.join(self.SHADER_DIRECTORY, 'flat', 'fragment_universal.glsl'),
                         priority=0)
        self.pv_id = None
        self.camera_transformation_id = None
        self.camera_pos_id = None
        self.object_diffuse_id = None
        self.object_reflectiveness_id = None
        self.object_glossiness_id = None
        self.object_transformation_id = None
        self.light_transformation_id = None
        self.light_pos_id = None
        self.light_color_id = None
        self.diffuse_sampler_id = None
        self.glossiness_sampler_id = None
        self.reflectiveness_sampler_id = None
        self.depth_sampler_id = None
        self.max_lights = max_lights
        self.vaos = {}

    def load(self):
        super().load()
        self.pv_id = glGetUniformLocation(self.program, "projectionView")
        self.camera_transformation_id = glGetUniformLocation(self.program, "cameraTransformation")
        self.camera_pos_id = glGetUniformLocation(self.program, "cameraPosition")
        self.object_diffuse_id = glGetUniformLocation(self.program, "objectDiffuse")
        self.object_reflectiveness_id = glGetUniformLocation(self.program, "objectReflectiveness")
        self.object_glossiness_id = glGetUniformLocation(self.program, "objectGlossiness")
        self.object_transformation_id = glGetUniformLocation(self.program, "objectTransformation")
        self.light_transformation_id = glGetUniformLocation(self.program, "lightTransformation")
        self.light_pos_id = glGetUniformLocation(self.program, "lightPosition")
        self.light_color_id = glGetUniformLocation(self.program, "lightColor")
        self.diffuse_sampler_id = glGetUniformLocation(self.program, "diffuseSampler")
        self.glossiness_sampler_id = glGetUniformLocation(self.program, "glossinessSampler")
        self.reflectiveness_sampler_id = glGetUniformLocation(self.program, "reflectivenessSampler")
        self.depth_sampler_id = glGetUniformLocation(self.program, "depthSampler")

    def render(self, objects: list[VisObject], lights: list[Light],
               projection_view_matrix: np.array, camera_position: np.array):
        self.begin()
        glUniformMatrix4fv(self.pv_id, 1, GL_FALSE, projection_view_matrix.T)
        glUniform3fv(self.camera_pos_id, 1, camera_position)
        for light in lights:
            # TODO: Define a light struct in fragment shader
            #  and handle multiple light sources!
            glUniform3fv(self.light_pos_id, 1, light.position)
            glUniform3fv(self.light_color_id, 1, light.color)
            if light.cast_shadows:
                glActiveTexture(GL_TEXTURE3)
                glBindTexture(GL_TEXTURE_2D, light.depth_map)
                glUniform1i(self.depth_sampler_id, 3)
                glUniformMatrix4fv(self.light_transformation_id, 1, GL_FALSE,
                light.get_transformation_matrix().T)

        for vis_object in objects:
            if vis_object.mesh.changed:
                vis_object.load_vbos()
                vis_object.mesh.changed = False

            self.bind_object(vis_object)

            glUniformMatrix4fv(self.object_transformation_id, 1, GL_FALSE,
                               vis_object.mesh.transformation.T)
            # glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, vis_object.indices_buffer)
            self.bind_material(vis_object)
            glDrawElements(
                GL_TRIANGLES,  # mode
                len(vis_object.mesh.triangle_indices) * 3,  # // count
                # TODO: check bigger type
                GL_UNSIGNED_INT,  # // type
                None  # // element array buffer offset
            )
            glBindVertexArray(0)
            # glDisableVertexAttribArray(0)
            # glDisableVertexAttribArray(1)
            # glDisableVertexAttribArray(2)
        self.end()

    def bind_material(self, vis_object):
        if isinstance(vis_object.material.diffuse, Texture):
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, vis_object.material.diffuse.texture_id)
            glUniform1i(self.diffuse_sampler_id, 0)
            glUniform3fv(self.object_diffuse_id, 1, np.array([-1, -1, -1]))
        else:
            glUniform3fv(self.object_diffuse_id, 1, vis_object.material.diffuse)


    def bind_buffers(self, vis_object):
        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, vis_object.vertex_buffer)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        # binding normal buffer
        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, vis_object.normal_buffer)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)

        # binding uv buffer
        if vis_object.mesh.uv is not None:
            glEnableVertexAttribArray(2)
            glBindBuffer(GL_ARRAY_BUFFER, vis_object.uv_buffer)
            glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, None)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, vis_object.indices_buffer)

    def bind_object(self, vis_object: VisObject):
        if vis_object in self.vaos:
            glBindVertexArray(self.vaos[vis_object])
        else:
            vao = glGenVertexArrays(1)
            glBindVertexArray(vao)
            self.bind_buffers(vis_object)
            # self.bind_material(vis_object)
            self.vaos[vis_object] = vao
