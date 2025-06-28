import glfw
from OpenGL.GL import *
import numpy as np
import random

class Triangle:
    def __init__(self, v1, v2, v3, color):
        self.vertices = [v1, v2, v3]
        self.color = color

temp_vertices = []
triangles = []

def generate_random_color():
    return (random.random(), random.random(), random.random())

def mouse_button_callback(window, button, action, mods):
    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
        x, y = glfw.get_cursor_pos(window)
        width, height = glfw.get_window_size(window)

        gl_x = (x / width) * 2 - 1
        gl_y = -((y / height) * 2 - 1)
        temp_vertices.append((gl_x, gl_y))

        if len(temp_vertices) == 3:
            color = generate_random_color()
            t = Triangle(temp_vertices[0], temp_vertices[1], temp_vertices[2], color)
            triangles.append(t)
            temp_vertices.clear()

def main():
    if not glfw.init():
        print("Erro ao inicializar GLFW.")
        return

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_COMPAT_PROFILE)


    window = glfw.create_window(800, 600, "Triângulos Interativos", None, None)
    if not window:
        print("Erro ao criar a janela.")
        glfw.terminate()
        return

    glfw.set_window_pos(window, 100, 100)
    glfw.make_context_current(window)
    glfw.set_mouse_button_callback(window, mouse_button_callback)

    while not glfw.window_should_close(window):
        glClearColor(0.1, 0.1, 0.15, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        for tri in triangles:
            glColor3f(*tri.color)
            glBegin(GL_TRIANGLES)
            for v in tri.vertices:
                glVertex2f(v[0], v[1])
            glEnd()

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

main()
