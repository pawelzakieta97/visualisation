import math
import time
from typing import Callable

import OpenGL.GLUT as oglut
import sys
import OpenGL.GL as gl
import OpenGL.GLU as glu


class GlutWindow:

    def __init__(self, width=800, height=480, window_name='window',
                 tick_func: Callable = None, target_fps=60, *args,
                 **kwargs):
        super().__init__()
        self.window = None
        self.width = width
        self.height = height
        self.window_name = window_name
        self.controller = None
        self.update_if = None  # oglut.glutPostRedisplay
        self.keyboard_state = []
        self.frame_number = 0
        self.last_fps_update = time.perf_counter()
        self.target_fps = target_fps
        self.tick_func = tick_func
        self.tick_duration_cum = 0
        self.render_duration_cum = 0

    def print_gpu_info(self):
        print(gl.glGetString(gl.GL_VENDOR))

    def init_opengl(self):
        oglut.glutInit(sys.argv)
        oglut.glutInitWindowSize(self.width, self.height)
        self.window = oglut.glutCreateWindow(self.window_name)
        oglut.glutInitDisplayMode(oglut.GLUT_RGBA | oglut.GLUT_DOUBLE | oglut.GLUT_DEPTH)
        print(self.width)
        self.print_gpu_info()
        gl.glClearColor(0.0, 0, 0.4, 0)
        gl.glDepthFunc(gl.GL_LESS)
        gl.glEnable(gl.GL_DEPTH_TEST)
        oglut.glutDisplayFunc(self.timerCallback)
        oglut.glutReshapeFunc(self.resize)
        oglut.glutKeyboardFunc(self.on_keyboard)
        oglut.glutKeyboardUpFunc(self.on_keyup)
        oglut.glutSpecialFunc(self.on_special_key)
        oglut.glutMouseFunc(self.on_mouse)
        oglut.glutMotionFunc(self.on_mousemove)
        oglut.glutSetOption(oglut.GLUT_ACTION_ON_WINDOW_CLOSE, oglut.GLUT_ACTION_CONTINUE_EXECUTION)

    def ogl_draw(self):
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        oglut.GLUT_KEY_UP
        glu.gluLookAt(4.0, 3.0, -3.0,
                      0.0, 0.0, 0.0,
                      0.0, 1.0, 0.0)
        # built in model
        oglut.glutSolidTeapot(1)

        print("please overrider ogl_draw")

    def display(self):
        dt = 1 / self.target_fps
        self.controller.on_keyboard(self.keyboard_state, dt)
        self.ogl_draw()
        oglut.glutSwapBuffers()
        oglut.glutPostRedisplay()

    def close(self):
        oglut.glutLeaveMainLoop()
        # oglut.glutDestroyWindow(self.window)

    def idle(self):
        pass

    def resize(self, Width, Height):
        print("please overrider resize")
        gl.glViewport(0, 0, Width, Height)
        glu.gluPerspective(45.0, float(Width) / float(Height), 0.1, 1000.0)

    def on_keyboard(self, key, x, y):
        key = key.decode()
        if key not in self.keyboard_state:
            self.keyboard_state.append(key)

    def on_special_key(self, key, x, y):
        if self.controller is not None:
            self.controller.on_special_key(key, x, y)
        else:
            print("please overrider on_keyboard")

    def on_mouse(self, *args, **kwargs):
        if self.controller is not None:
            self.controller.on_mouse(*args, **kwargs)
        else:
            print("please overrider on_mouse")

    def on_mousemove(self, *args, **kwargs):
        if self.controller != None:
            self.controller.on_mousemove(*args, **kwargs)
        else:
            print("please overrider on_mousemove")

    def on_keyup(self, key, x, y):
        key = key.decode()
        if key in self.keyboard_state:
            self.keyboard_state.remove(key)

    def run(self, tick_func=None):
        if tick_func is not None:
            self.tick_func = tick_func
        # self.timerCallback()
        oglut.glutMainLoop()

    def timerCallback(self, *args, **kwargs):
        start = time.perf_counter()
        self.frame_number += 1
        tick_duration = 0
        if self.tick_func is not None:
            s = time.perf_counter()
            self.tick_func()
            tick_duration = time.perf_counter() - s
            self.tick_duration_cum += tick_duration
        s = time.perf_counter()
        self.display()
        render_duration = time.perf_counter() - s
        self.render_duration_cum += render_duration
        title_update_period = 30
        if self.frame_number % title_update_period == 0:
            now = time.perf_counter()
            fps = math.floor(title_update_period / (now - self.last_fps_update))
            self.last_fps_update = now
            tick_time = self.tick_duration_cum / title_update_period
            render_time = self.render_duration_cum / title_update_period
            title = f'{self.window_name} {fps} fps. ' \
                    f'\ttick {str(tick_time * 1000)[:6]}ms' \
                    f'\trender {str(render_time * 1000)[:6]}ms' \
                    f'\tusage {int((tick_time + render_time) * fps * 100)}%'
            oglut.glutSetWindowTitle(title)
            # print(title)
            self.tick_duration_cum = 0
            self.render_duration_cum = 0
        sleep_time = max(0.0, 1 / self.target_fps - (time.perf_counter() - start))
        time.sleep(sleep_time)


if __name__ == "__main__":
    win = GlutWindow()
    win.run()
