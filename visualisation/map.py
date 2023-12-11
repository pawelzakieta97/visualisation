import numpy as np
from OpenGL.GL import *  # pylint: disable=W0614

from models.mesh import Mesh
from visualisation.light import Light
from visualisation.renderable import Renderable
from visualisation.visobject import VisObject


class Map(VisObject):
    def __init__(self, data: np.array, auto_reload=True):
        mesh = Mesh(vertices=np.array([[0, 0, 0],
                                       [1, 0, 0],
                                       [1, 1, 0],
                                       [0, 1, 0]]),
                    triangle_indices=np.array([[0, 1, 2], [2, 3, 0]]),
                    uv=np.array([[0, 0],
                                 [1, 0],
                                 [1, 1],
                                 [0, 1]]))
        super().__init__(mesh)
        self.data = data
        self.auto_reload = auto_reload

    def render(self, projection_matrix, view_matrix, camera_position, light):
        self.shader.begin()
        glUniformMatrix4fv(self.MVP_ID, 1, GL_FALSE, (projection_matrix @ np.linalg.inv(view_matrix)).T)

        glUniformMatrix4fv(self.object_transformation_id, 1, GL_FALSE,
                           self.mesh.transformation.T)

        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.uv_buffer)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.material.texture_id)
        glUniform1i(self.TextureID, 0)
        # glUniform1i(self.context.TextureID, 0)

        glEnableVertexAttribArray(2)
        glBindBuffer(GL_ARRAY_BUFFER, self.normal_buffer)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, None)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.indices_buffer)
        glDrawElements(
            GL_TRIANGLES,  # mode
            len(self.mesh.triangle_indices) * 3,  # // count
            # TODO: check bigger type
            GL_UNSIGNED_SHORT,  # // type
            None  # // element array buffer offset
        )

        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)
        glDisableVertexAttribArray(2)
        self.shader.end()
