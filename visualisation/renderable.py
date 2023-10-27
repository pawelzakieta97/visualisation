from visualisation.shader import Shader


class Renderable(object):
    SHADER_DIRECTORY = 'visualisation/glsl'

    def __init__(self):
        self.shader = None

    def makeContext(self):
        self.load_shader()
        self.load_object()
        # self.loadTexture()
        return self

    def load_shader(self):
        self.shader = Shader()

    def load_object(self):
        print("Make and fill OPENGL buffers,vertex,uv,normal,trangent,indices")

    def render(self, VP, camera_position, lights):
        print("override rendering process")
        pass
