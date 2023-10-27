

from OpenGL.GL import *  # pylint: disable=W0614
from OpenGL.GLUT import *  # pylint: disable=W0614

from visualisation.MVPControl import MVPController
from visualisation.floorgrid import FloorGrid
from visualisation.glutWindow import GlutWindow
from visualisation.light import Light
from visualisation.renderable import Renderable


# from glutWindow import GlutWindow
# from MVPControl import MVPController
# from utils.shaderLoader import Shader


class MeshViewWindow(GlutWindow):
    def __init__(self, light: Light = None, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.projection_matrix = None
        self.menu = None
        self.vis_objects = []
        self.light = light

    def init_opengl(self):
        glClearColor(0.1, 0.1, 0.1, 0.8)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        #glEnable(GL_CULL_FACE)

    def add_object(self, vis_object: Renderable):
        self.vis_objects.append(vis_object.makeContext())

    def init_context(self):        
        self.vis_objects = []

    def update_projection_matrix(self, width=0, height=0):
        
        if width != 0:
            self.controller.resize(width, height)
        # self.projection_matrix = glm.mat4x4(self.controller.get_VP())
        self.projection_matrix = self.controller.get_VP()

    def resize(self, width, height):  
        print("resize")
        glViewport(0, 0, width, height)
        self.update_projection_matrix(width, height)

    def ogl_draw(self):
        self.update_projection_matrix()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for mesh in self.vis_objects:
            mesh.render(self.projection_matrix, self.controller.pos, None)
            
    def processMenuEvents(self, *args, **kwargs):
        action, = args

        if action == 3:
            self.controller.reset()
            self.update_if() 
        if action == 2:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            self.update_if()
        if action == 4:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)    
            self.update_if()        
        return 0

    def init_default(self):
        self.controller = MVPController(self.update_if)
        self.init_opengl()
        self.init_context()    
        self.add_object(FloorGrid())
        self.menu = glutCreateMenu(self.processMenuEvents)
        glutAddMenuEntry("UV MAP", 1)
        glutAddMenuEntry("WireFrame Mode", 2)
        glutAddMenuEntry("GL_FILL Mode", 4)
        glutAddMenuEntry("Reset View", 3)
        glutAttachMenu(GLUT_RIGHT_BUTTON)
        return self

