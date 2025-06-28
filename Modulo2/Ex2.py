import glfw
from OpenGL.GL import *
import numpy as np

def createTriangle(x0, y0, x1, y1, x2, y2):
    vertices = np.array([
        x0, y0,
        x1, y1,
        x2, y2
    ], dtype=np.float32)
    
    vao =glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    
    glBindVertexArray(vao)
        
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, None)
    
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)
    
    return vao

if not glfw.init():
    raise Exception("Falha ao criar janela")

window = glfw.create_window(600, 600, "Triangulos", None, None)
if not window:
    glfw.terminate()
    raise Exception("Falha ao criar janela")

glfw.make_context_current(window)

triangle_vaos = [
    createTriangle(-0.8, -0.8, -0.6, -0.8, -0.7, -0.6),
    createTriangle(-0.4, -0.8, -0.2, -0.8, -0.3, -0.6),
    createTriangle(0.0, -0.8, 0.2, -0.8, 0.1, -0.6),
    createTriangle(0.4, -0.8, 0.6, -0.8, 0.5, -0.6),
    createTriangle(0.0, 0.0, 0.2, 0.0, 0.1, 0.2)
]

while not glfw.window_should_close(window):
    glClear(GL_COLOR_BUFFER_BIT)
    
    for vao in triangle_vaos:
        glBindVertexArray(vao)
        glDrawArrays(GL_TRIANGLES, 0, 3)
        
    glfw.swap_buffers(window)
    glfw.poll_events()
    
glfw.terminate()