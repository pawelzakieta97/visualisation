import math
import time

import OpenGL.GLUT as oglut
import sys
import OpenGL.GL as gl
import OpenGL.GLU as glu

class GlutWindow(object):

    def print_gpu_info(self):
        print(gl.glGetString(gl.GL_VENDOR))

    def init_opengl(self):
        self.print_gpu_info()
        gl.glClearColor(0.0,0,0.4,0)
        gl.glDepthFunc(gl.GL_LESS)
        gl.glEnable(gl.GL_DEPTH_TEST)
        
    def ogl_draw(self):
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        oglut.GLUT_KEY_UP
        glu.gluLookAt(4.0,3.0,-3.0, 
                0.0,0.0,0.0,
                0.0,1.0,0.0)
        #built in model
        oglut.glutSolidTeapot(1)

        print("please overrider ogl_draw")

    def display(self):
        dt = 1/self.target_fps
        self.controller.on_keyboard(self.keyboard_state, dt)
        self.ogl_draw()
        oglut.glutSwapBuffers()

    def idle(self):
        pass

    def resize(self,Width,Height):
        print("please overrider resize")
        gl.glViewport(0, 0, Width, Height)
        glu.gluPerspective(45.0, float(Width)/float(Height), 0.1, 1000.0)        

    def on_keyboard(self,key,x,y):
        key = key.decode()
        if key not in self.keyboard_state:
            self.keyboard_state.append(key)

    def on_special_key(self,key,x,y):     
        if(self.controller!=None):
              self.controller.on_special_key(key,x,y)
        else:
            print("please overrider on_keyboard")

    def on_mouse(self,*args,**kwargs):
        if(self.controller!=None):
              self.controller.on_mouse(*args,**kwargs)
        else:
            print("please overrider on_mouse")

    def on_mousemove(self,*args,**kwargs):
        if(self.controller!=None):
              self.controller.on_mousemove(*args,**kwargs)
        else:
            print("please overrider on_mousemove")

    def on_keyup(self, key,x,y):
        key = key.decode()
        if key in self.keyboard_state:
            self.keyboard_state.remove(key)

    def __init__(self, width=800, height=480, window_name='window', *args, **kwargs):
        oglut.glutInit(sys.argv)
        oglut.glutInitDisplayMode(oglut.GLUT_RGBA | oglut.GLUT_DOUBLE | oglut.GLUT_DEPTH)
        oglut.glutInitWindowSize(width, height)
        self.window_name = window_name
        self.window = oglut.glutCreateWindow(self.window_name)
        oglut.glutDisplayFunc(self.display)
        #oglut.glutIdleFunc(self.display) 
        oglut.glutReshapeFunc(self.resize)
        oglut.glutKeyboardFunc(self.on_keyboard)
        oglut.glutKeyboardUpFunc(self.on_keyup)
        oglut.glutSpecialFunc(self.on_special_key)  
        oglut.glutMouseFunc(self.on_mouse)
        oglut.glutMotionFunc(self.on_mousemove)
        self.controller = None
        self.update_if = None #oglut.glutPostRedisplay
        self.keyboard_state = []
        self.frame_number = 0
        self.last_fps_update = time.perf_counter()
        self.target_fps = 60

    def run(self):
        self.timerCallback()
        oglut.glutMainLoop()

    def timerCallback(self, *args, **kwargs):
        self.frame_number += 1
        numFpsFrames = 30
        currentTime = time.perf_counter()

        if self.frame_number % numFpsFrames == 0:
            passedTime = currentTime - self.last_fps_update
            self.last_fps_update = currentTime
            fps = math.floor(numFpsFrames / passedTime)
            oglut.glutSetWindowTitle(self.window_name + ' ' + str(fps) + " fps")
        self.display()
        render_time = (time.perf_counter() - currentTime) * 1000
        oglut.glutTimerFunc(max(0, math.floor((1000.0 / self.target_fps) - render_time)), self.timerCallback, 0)


if __name__ == "__main__":
    win = GlutWindow()
    win.run()