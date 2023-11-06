import threading
from typing import Any, Union

from OpenGL.GL import *  # pylint: disable=W0614
from OpenGL.GLUT import *  # pylint: disable=W0614

from transformations import get_orthographic_projection_matrix
from visualisation.MVPControl import MVPController
from models.floorgrid import FloorGrid
from visualisation.glutWindow import GlutWindow
from visualisation.light import Light
from visualisation.renderable import Renderable
from visualisation.renderable_factory import get_renderable


class MeshViewWindow(GlutWindow):
    def __init__(self, light: Light = None, add_floorgrid=False, orthographic=False,
                 *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.projection_matrix = None
        self.menu = None
        self.vis_objects = []
        self.light = light
        self.controller = MVPController(orthographic=orthographic)
        if add_floorgrid:
            floor_model = FloorGrid()
            self.add_object(floor_model)

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
        #glEnable(GL_CULL_FACE)

    def add_object(self, model: Union[Renderable, Any]):
        if not isinstance(model, Renderable):
            model = get_renderable(model)
        self.vis_objects.append(model)

    def update_projection_matrix(self, width=0, height=0):
        
        if width != 0:
            self.controller.resize(width, height)
        # self.projection_matrix = glm.mat4x4(self.controller.get_VP())
        # self.projection_matrix = self.controller.get_VP()

    def resize(self, width, height):  
        print("resize")
        glViewport(0, 0, width, height)
        self.update_projection_matrix(width, height)

    def ogl_draw(self):
        self.update_projection_matrix()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for mesh in self.vis_objects:
            pm = self.controller.get_projection_matrix()
            mesh.render(pm, self.controller.get_view_matrix(), self.controller.get_pos(), None)
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

    def run(self):
        self.init_opengl()
        for obj in self.vis_objects:
            obj.makeContext()
        super().run()