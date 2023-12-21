import threading
import time
from typing import Any, Union

import numpy as np
from OpenGL.GL import *  # pylint: disable=W0614
from OpenGL.GLUT import *  # pylint: disable=W0614

from models.multi_mesh import merge_meshes
from visualisation.MVPControl import MVPController
from models.floorgrid import FloorGrid
from visualisation.glutWindow import GlutWindow
from visualisation.light import Light
from visualisation.renderable import Renderable
from visualisation.renderable_factory import get_renderable
from visualisation.shader import Shader
from visualisation.visobject import VisObject


class MeshViewWindow(GlutWindow):
    def __init__(self, light: Light = None, add_floorgrid=False, orthographic=False,
                 enable_control: bool = True,
                 **kwargs):

        super().__init__(**kwargs)

        self.depth_buffer = None
        self.projection_matrix = None
        self.menu = None
        self.vis_objects = []
        if light is None or not light:
            light = Light(position=np.array([-5, 10, -7]), color=np.array([1, 1, 1]))

        self.light = light
        self.controller = MVPController(orthographic=orthographic, enable_control=enable_control)
        self.depth_shader = Shader()
        if add_floorgrid:
            floor_model = FloorGrid()
            self.add_object(floor_model)
        self.MVP_ID = None
        self.object_transformation_id = None
        self.camera_transformation_id = None

    def init_opengl(self):
        super().init_opengl()
        self.menu = glutCreateMenu(self.processMenuEvents)
        glutAddMenuEntry("UV MAP", 1)
        glutAddMenuEntry("WireFrame Mode", 2)
        glutAddMenuEntry("GL_FILL Mode", 4)
        glutAddMenuEntry("Reset View", 3)
        glutAddMenuEntry("Perspective", 5)
        glutAddMenuEntry("Orthographic", 6)
        glutAttachMenu(GLUT_RIGHT_BUTTON)
        glClearColor(0.1, 0.1, 0.1, 0.8)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        self.depth_shader.initShaderFromGLSL([os.path.join(VisObject.SHADER_DIRECTORY, 'shadow', 'vertex.glsl')],
                                             [os.path.join(VisObject.SHADER_DIRECTORY, 'shadow', 'fragment.glsl')])
        self.MVP_ID = glGetUniformLocation(self.depth_shader.program, "MVP")
        self.camera_transformation_id = glGetUniformLocation(self.depth_shader.program, "cameraTransformation")
        self.object_transformation_id = glGetUniformLocation(self.depth_shader.program, "objectTransformation")

        self.depth_buffer = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.depth_buffer)
        glDrawBuffer(GL_NONE)
        glReadBuffer(GL_NONE)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        #glEnable(GL_CULL_FACE)

    def add_object(self, model: Union[Renderable, Any], *args, **kwargs):
        if not isinstance(model, Renderable):
            model = get_renderable(model, *args, **kwargs)
        self.vis_objects.append(model)
        return model

    def update_projection_matrix(self, width=0, height=0):
        if width != 0:
            self.controller.resize(width, height)

    def resize(self, width, height):  
        print("resize")
        self.width, self.height = width, height
        glViewport(0, 0, width, height)
        self.update_projection_matrix(width, height)

    def draw_depth_map(self, merge_objs=False):
        self.depth_shader.begin()

        glViewport(0, 0, self.light.res, self.light.res)
        glBindFramebuffer(GL_FRAMEBUFFER, self.depth_buffer)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D,
                               self.light.depth_map, 0)
        glClear(GL_DEPTH_BUFFER_BIT)
        mvp = self.light.get_transformation_matrix()
        # mvp = self.controller.get_projection_matrix() @ np.linalg.inv(self.controller.get_view_matrix())
        glUniformMatrix4fv(self.MVP_ID, 1, GL_FALSE, mvp.T)
        # TODO: faster to merge objects to render with fewer calls??
        shadow_casters = [o for o in self.vis_objects if o.casts_shadows]
        if merge_objs:
            merged = VisObject(merge_meshes([vo.mesh for vo in shadow_casters], as_mesh=True))
            merged.load()
            shadow_casters = [merged]
        for vis_obj in shadow_casters:
            glUniformMatrix4fv(self.object_transformation_id, 1, GL_FALSE,
                               vis_obj.mesh.transformation.T)

            glEnableVertexAttribArray(0)
            glBindBuffer(GL_ARRAY_BUFFER, vis_obj.vertex_buffer)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, vis_obj.indices_buffer)
            glDrawElements(
                GL_TRIANGLES,  # mode
                len(vis_obj.mesh.triangle_indices) * 3,  # // count
                # TODO: check bigger type
                GL_UNSIGNED_INT,  # // type
                None  # // element array buffer offset
            )

        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        self.depth_shader.end()

    def ogl_draw(self):
        self.update_projection_matrix()
        if self.light is not None and self.light.cast_shadows:
            self.draw_depth_map()
            pass
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glViewport(0, 0, self.width, self.height)
        pm = self.controller.get_projection_matrix()
        vm = self.controller.get_view_matrix()
        mvp = pm @ np.linalg.inv(vm)
        for mesh in self.vis_objects:
            mesh.render(mvp, self.controller.get_pos(), self.light)
            pass
            # mesh.render(self.controller.projection_matrix, self.controller.view_matrix, self.controller.pos, None)
            
    def processMenuEvents(self, *args, **kwargs):
        action, = args
        if action == 3:
            self.controller.reset_view()
        if action == 2:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        if action == 4:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        if action == 5:
            self.controller.orthographic = False
        if action == 6:
            self.controller.orthographic = True
        return 0

    def run(self, tick_func=None):
        self.tick_func = tick_func
        self.init_opengl()
        for obj in self.vis_objects:
            obj.load()
        self.light.load()
        super().run(tick_func)
