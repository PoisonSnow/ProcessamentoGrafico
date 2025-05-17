from OpenGL.GL import *
import numpy as np
import glfw

def createTriangle(x0, y0, x1, y1, x2, y2):
    vertices = np.array([x0, y0, 0.0,  # Vértice 0
                         x1, y1, 0.0,  # Vértice 1
                         x2, y2, 0.0], # Vértice 2
                        dtype=np.float32)
    
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER,vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)
    
    glBindVertexArray(0)
    
    return vao
if not glfw.init():
    raise Exception("Erro GLFW")

window = glfw.create_window(800, 600, "Triangulo", None, None)
if not window:
    glfw.terminate()
    raise Exception("Erro ao criar janela")

glfw.make_context_current(window)

vao = createTriangle(-0.5, -0.5, 0.5, -0.5, 0.0, 0.5)
print("VAO gerado:", vao)

while not glfw.window_should_close(window):
    glClear(GL_COLOR_BUFFER_BIT)
    
    glBindVertexArray(vao)
    glDrawArrays(GL_TRIANGLES, 0, 3)
    glBindVertexArray(0)
    
    glfw.swap_buffers(window)
    glfw.poll_events()

glfw.terminate()