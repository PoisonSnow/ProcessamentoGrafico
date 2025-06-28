import glfw
from OpenGL.GL import *
import numpy as np

# Shaders
vertex_shader_src = """
#version 330 core
layout (location = 0) in vec2 aPos;
layout (location = 1) in vec3 aColor;
out vec3 ourColor;
uniform mat4 transform;
void main() {
    gl_Position = transform * vec4(aPos, 0.0, 1.0);
    ourColor = aColor;
}
"""

fragment_shader_src = """
#version 330 core
in vec3 ourColor;
out vec4 FragColor;
void main() {
    FragColor = vec4(ourColor, 1.0);
}
"""
glfw.init()
window = glfw.create_window (1200, 600, "Jogo das cores", None, None)
glfw.make_context_current(window)

def compile_shader(type, source):
    shader = glCreateShader(type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    return shader

vs = compile_shader(GL_VERTEX_SHADER, vertex_shader_src)
fs = compile_shader(GL_FRAGMENT_SHADER, fragment_shader_src)
shader_program = glCreateProgram()
glAttachShader(shader_program, vs)
glAttachShader(shader_program, fs)
glLinkProgram(shader_program)

cols, rows = 10, 8
rect_w, rect_h = 2.0 / cols, 2.0 / rows
pontuacao = 0
tentativas = 0
retangulos = []

def generate_grid():
    global retangulos, pontuacao, tentativas
    retangulos = []
    pontuacao = 0
    tentativas = 0
    for y in range(rows):
        for x in range(cols):
            xpos = -1 + x * rect_w
            ypos = -1 + y * rect_h
            color = np.random.rand(3) 
            retangulos.append({'x': xpos, 'y': ypos, 'color': color, 'visible': True})
            
generate_grid()

def create_rect_verticles(x, y, w, h, color):
    return np.array([
        [x, y, *color],
        [x + w, y, *color],
        [x + w, y + h, *color],
        [x, y, *color],
        [x + w, y + h, *color],
        [x, y + h, *color],
    ], dtype=np.float32)
    
def color_similarity(c1, c2, scale_factor=0.6):
    return np.linalg.norm(np.array(c1) - np.array(c2)) * scale_factor

vao = glGenVertexArrays(1)
vbo = glGenBuffers(1)

def draw_retangulos():
    glUseProgram(shader_program)
    glBindVertexArray(vao)
    for rect in retangulos:
        if not rect['visible']:
            continue
        verts = create_rect_verticles(rect['x'], rect['y'], rect_w, rect_h, rect['color'])
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_DYNAMIC_DRAW)
        
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 5* 4, ctypes.c_void_p(8))
        
        transform_loc = glGetUniformLocation(shader_program, "transform")
        glUniformMatrix4fv(transform_loc, 1, GL_FALSE, np.identity(4, dtype=np.float32))
        glDrawArrays(GL_TRIANGLES, 0, 6)
        
def mouse_button_callback(window, button, action, mods):
    global pontuacao, tentativas
    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
        xpos, ypos, = glfw.get_cursor_pos(window)
        w, h = glfw.get_window_size(window)
        ndc_x = ((xpos / w) * 2 - 1)
        ndc_y = -((ypos / h)* 2 - 1)
        
        clicked_color = None
        for rect in retangulos:
            if rect ['visible']:
                if rect['x'] <= ndc_x <= rect['x'] + rect_w and rect['y'] <= ndc_y <= rect['y'] + rect_h:
                    clicked_color = rect['color']
                    break
        if clicked_color is not None:
            removed = 0
            for rect in retangulos:
                if rect['visible'] and color_similarity(clicked_color, rect['color']) < 0.25:
                    rect['visible'] = False
                    removed += 1

            if removed > 0:
                pontuacao += removed * 10
                if removed > 5:
                    pontuacao += 20 
            tentativas += 1
            if tentativas > 1:
                pontuacao -= 2 * (tentativas - 1)
            pontuacao = max(0, min(1000, pontuacao))
            
def key_callback(window, key, scancode, action, mods):
    if key == glfw.KEY_R and action == glfw.PRESS:
        generate_grid()
        
glfw.set_mouse_button_callback(window, mouse_button_callback)
glfw.set_key_callback(window, key_callback)

while not glfw.window_should_close(window):
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)
    
    draw_retangulos()
    
    glfw.swap_buffers(window)
    glfw.poll_events()

print("Pontuação final:", pontuacao)
glfw.terminate()