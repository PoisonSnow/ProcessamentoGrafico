import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
import numpy as np

tile_width, tile_height = 128, 64
map_size = 3

tile_map = [
    [1, 2, 1],
    [2, 1, 2],
    [1, 2, 1]
]

window_width, window_height = 800, 600

if not glfw.init():
    raise Exception("Falha ao iniciar o GLFW")

window = glfw.create_window(window_width, window_height, "Mapa Isométrico com Sprite", None, None)
if not window:
    glfw.terminate()
    raise Exception("Não foi possível criar a janela")

glfw.make_context_current(window)

def setup_projection():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glClearColor(245/255.0, 245/255.0, 220/255.0, 1.0)

setup_projection()

def load_texture(path):
    img = Image.open(path).convert("RGBA").transpose(Image.FLIP_TOP_BOTTOM)
    img_data = np.array(img)

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    return tex_id, img.width, img.height

texture_id, tex_width, tex_height = load_texture("TileSet.png")
character_texture_id, char_tex_width, char_tex_height = load_texture("Char.png")
glEnable(GL_TEXTURE_2D)

tiles_in_row = tex_width // tile_width

def draw_tile(i, j, tile_index):
    iso_x = (i - j) * (tile_width // 2)
    iso_y = (i + j) * (tile_height // 2)

    center_x = window_width // 2
    center_y = window_height // 2 - map_size * (tile_height // 2)

    glBindTexture(GL_TEXTURE_2D, texture_id)
    glColor3f(1.0, 1.0, 1.0)

    glPushMatrix()
    glTranslatef(center_x + iso_x, center_y + iso_y, 0)

    u = (tile_index % tiles_in_row) * (tile_width / tex_width)
    v = 0
    du = tile_width / tex_width
    dv = tile_height / tex_height

    glBegin(GL_QUADS)
    glTexCoord2f(u + du / 2, v + dv)
    glVertex2f(0, tile_height / 2)

    glTexCoord2f(u + du, v + dv / 2)
    glVertex2f(tile_width / 2, 0)

    glTexCoord2f(u + du / 2, v)
    glVertex2f(0, -tile_height / 2)

    glTexCoord2f(u, v + dv / 2)
    glVertex2f(-tile_width / 2, 0)
    glEnd()

    glPopMatrix()

def draw_character(x, y):
    iso_x = (x - y) * (tile_width // 2)
    iso_y = (x + y) * (tile_height // 2)

    center_x = window_width // 2
    center_y = window_height // 2 - map_size * (tile_height // 2)

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, character_texture_id)
    glColor3f(1.0, 1.0, 1.0)

    glPushMatrix()
    glTranslatef(center_x + iso_x, center_y + iso_y + tile_height // 2, 0)

    sprite_width = tile_width // 2
    sprite_height = tile_height

    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(-sprite_width // 2, -sprite_height // 2)

    glTexCoord2f(1, 0)
    glVertex2f(sprite_width // 2, -sprite_height // 2)

    glTexCoord2f(1, 1)
    glVertex2f(sprite_width // 2, sprite_height // 2)

    glTexCoord2f(0, 1)
    glVertex2f(-sprite_width // 2, sprite_height // 2)
    glEnd()

    glPopMatrix()

def draw_map():
    for i in range(map_size):
        for j in range(map_size):
            draw_tile(i, j, tile_map[i][j])

character_x, character_y = map_size // 2, map_size // 2

def move_character(dx, dy):
    global character_x, character_y
    new_x = character_x + dx
    new_y = character_y + dy
    if 0 <= new_x < map_size and 0 <= new_y < map_size:
        character_x, character_y = new_x, new_y

def keyboard_input(window, key, scancode, action, mods):
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_D:
            move_character(0, -1)
        elif key == glfw.KEY_A:
            move_character(0, 1)
        elif key == glfw.KEY_S:
            move_character(-1, 0)
        elif key == glfw.KEY_W:
            move_character(1, 0)
        elif key == glfw.KEY_C:
            move_character(-1, -1)
        elif key == glfw.KEY_E:
            move_character(1, -1)
        elif key == glfw.KEY_Z:
            move_character(-1, 1)
        elif key == glfw.KEY_Q:
            move_character(1, 1)

glfw.set_key_callback(window, keyboard_input)

def render():
    glClear(GL_COLOR_BUFFER_BIT)
    draw_map()
    draw_character(character_x, character_y)
    glfw.swap_buffers(window)

while not glfw.window_should_close(window):
    glfw.poll_events()
    render()

glfw.terminate()