import glfw
from OpenGL.GL import *
import numpy as np
import random
import glm


class Triangle:
    def __init__(self, position, color):
        self.position = position
        self.color = color
        
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

def compile_shader(vertex_src, fragment_src):
    vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertex_shader, vertex_src)
    glCompileShader(vertex_shader)
    
    if not glGetShaderiv(vertex_shader, GL_COMPILE_STATUS):
        print("Erro ao compilar o vertex shader: ", glGetShaderInfoLog(vertex_shader))
        return None
    
    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragment_shader, fragment_src)
    glCompileShader(fragment_shader)
    
    if not glGetShaderiv(fragment_shader, GL_COMPILE_STATUS):
        print("Erro ao compilar", glGetShaderInfoLog(fragment_shader))
        return None
    
    shader_program = glCreateProgram()
    glAttachShader(shader_program, vertex_shader)
    glAttachShader(shader_program, fragment_shader)
    glLinkProgram(shader_program)
    
    if not glGetProgramiv(shader_program, GL_LINK_STATUS):
        print("Erro ao linkar o programa de shader:", glGetProgramInfoLog(shader_program))
        return None
    
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)
    
    return shader_program

def mouse_click(window, button, action, mods):
    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
        x, y = glfw.get_cursor_pos(window)
        width, height = glfw.get_framebuffer_size(window)
        
        norm_x = (x / width) * 2 - 1
        norm_y = 1 - (y / height) * 2
        
        color = [random.random() for _ in range(3)]
        
        new_vao = createTriangle(norm_x - 0.1, norm_y - 0.1, norm_x + 0.1, norm_y - 0.1, norm_x, norm_y + 0.1)
        triangles.append(Triangle(glm.vec2(norm_x, norm_y), color))


if not glfw.init():
    raise Exception("Falha ao criar janela")

window = glfw.create_window(600, 600, "Triangulos", None, None)
if not window:
    glfw.terminate()
    raise Exception("Falha ao criar janela")

glfw.make_context_current(window)
glfw.set_mouse_button_callback(window, mouse_click)

# Código do Vertex Shader
vertex_shader_src = """
#version 330 core
layout(location = 0) in vec2 aPos;
void main() {
    gl_Position = vec4(aPos, 0.0, 1.0);
}
"""

# Código do Fragment Shader
fragment_shader_src = """
#version 330 core
out vec4 FragColor;
uniform vec3 uColor;
void main() {
    FragColor = vec4(uColor, 1.0);
}
"""

shader_program = compile_shader(vertex_shader_src, fragment_shader_src)
if not shader_program:
    glfw.terminate()
    raise Exception("Falha ao compilar e vincular os shaders")

triangles = [
    Triangle(glm.vec2(-0.8, -0.8), [random.random() for _ in range(3)]),
    Triangle(glm.vec2(-0.4, -0.8), [random.random() for _ in range(3)]),
    Triangle(glm.vec2(0.0, -0.8), [random.random() for _ in range(3)]),
    Triangle(glm.vec2(0.4, -0.8), [random.random() for _ in range(3)]),
    Triangle(glm.vec2(0.0, 0.0), [random.random() for _ in range(3)]),
]

default_vao = createTriangle(-0.1, -0.1, 0.1, -0.1, 0.0, 0.1)
glUseProgram(shader_program)

while not glfw.window_should_close(window):
    glClear(GL_COLOR_BUFFER_BIT)
    
    for triangle in triangles:
        uColor_loc = glGetUniformLocation(shader_program, "uColor")
        glUniform3f(uColor_loc, *triangle.color) 
        
        glBindVertexArray(default_vao)
        glDrawArrays(GL_TRIANGLES, 0, 3)
    
    glfw.swap_buffers(window)
    glfw.poll_events()

glfw.terminate()