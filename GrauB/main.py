import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import random
from tilemap import TileMap

TILE_TEXTURES = {
    "preto": "textures/preto.png",
    "pedra": "textures/pedra.png",
    "lava":  "textures/lava.png",
    "couro": "textures/couro.png",
}

SPRITE_VERTEX_SHADER = """
#version 330
in vec2 position;
in vec2 texcoord;
out vec2 vTexcoord;
uniform vec2 offset;
uniform vec2 scale;
void main() {
    gl_Position = vec4((position * scale) + offset, 0.0, 1.0);
    vTexcoord = texcoord;
}
"""

SPRITE_FRAGMENT_SHADER = """
#version 330
in vec2 vTexcoord;
out vec4 outColor;
uniform sampler2D tileTexture;
void main() {
    outColor = texture(tileTexture, vTexcoord);
}
"""

def iso_pos(row, col, width, height, tile_px_w, tile_px_h, screen_w, screen_h):
    row_flipped = height - 1 - row
    cx = screen_w // 2
    cy = tile_px_h // 2
    screen_x = (col - row_flipped) * (tile_px_w // 2)
    screen_y = (col + row_flipped) * (tile_px_h // 2)
    return ((screen_x + cx) / (screen_w / 2) - 1,
            0.8 - (screen_y + cy) / (screen_h / 2))

def make_diamond_quad(tile_width, tile_height):
    hw = tile_width / 2
    hh = tile_height / 2
    return np.array([
        [0,   -hh, 0.5, 0.0],  # Top
        [ hw,  0,  1.0, 0.5],  # Right
        [0,    hh, 0.5, 1.0],  # Bottom
        [-hw,  0,  0.0, 0.5],  # Left
    ], dtype=np.float32), np.array([0,1,2, 2,3,0], dtype=np.uint32)

def make_rect_quad(width, height):
    hw = width / 2
    hh = height / 2
    return np.array([
        [-hw, -hh, 0.0, 0.0],  # Bottom Left
        [ hw, -hh, 1.0, 0.0],  # Bottom Right
        [ hw,  hh, 1.0, 1.0],  # Top Right
        [-hw,  hh, 0.0, 1.0],  # Top Left
    ], dtype=np.float32), np.array([0,1,2, 2,3,0], dtype=np.uint32)

def load_texture(path):
    surface = pygame.image.load(path).convert_alpha()
    image = pygame.image.tostring(surface, "RGBA", True)
    width, height = surface.get_size()
    texid = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texid)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glBindTexture(GL_TEXTURE_2D, 0)
    return texid

def load_spritesheet(path, frame_width, frame_height, frame_count):
    surface = pygame.image.load(path).convert_alpha()
    frames = []
    for i in range(frame_count):
        frame_surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        frame_surface.blit(surface, (0, 0), (i * frame_width, 0, frame_width, frame_height))
        image = pygame.image.tostring(frame_surface, "RGBA", True)
        texid = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texid)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, frame_width, frame_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glBindTexture(GL_TEXTURE_2D, 0)
        frames.append(texid)
    return frames

def draw_text(surface, text, pos, color=(255,255,255), font_size=48, center=True):
    font = pygame.font.SysFont("Arial", font_size, bold=True)
    render = font.render(text, True, color)
    rect = render.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surface.blit(render, rect)

def random_couro_positions(tilemap, n=5):
    pedra_tiles = [(row, col)
                   for row in range(1, tilemap.height)
                   for col in range(tilemap.width)
                   if tilemap.tiles[row][col] == "pedra"]
    return random.sample(pedra_tiles, n)

def reset_game():
    tilemap = TileMap.generate_varied_branching_paths(15, 15, player_sprite="textures/player.png")
    player = tilemap.player
    vidas = 5
    game_over = False
    venceu = False
    last_safe_pos = (player.row, player.col)
    couro_positions = set(random_couro_positions(tilemap, n=5))
    couro_coletado = set()
    tem_bota = False
    caminho_oculto = False
    ciclo_passos = [False, True, True]
    ciclo_idx = 0
    return (tilemap, player, vidas, game_over, venceu, last_safe_pos,
            couro_positions, couro_coletado, tem_bota, caminho_oculto, ciclo_passos, ciclo_idx)

def main():
    screen_w, screen_h = 1920, 1080
    tile_px_w, tile_px_h = 128, 64

    pygame.init()
    pygame.display.set_mode((screen_w, screen_h), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Mapa Isométrico (Diamond)")
    pygame.font.init()
    screen_surf = pygame.display.get_surface()

    # --- Textures and resources ---
    tile_textures = {}
    for tiletype, path in TILE_TEXTURES.items():
        if tiletype != "couro":
            tile_textures[tiletype] = load_texture(path)
    couro_texture = load_texture(TILE_TEXTURES["couro"])

    # ---- SPRITE ANIMATION CONFIG ----
    PLAYER_FRAME_W = 64
    PLAYER_FRAME_H = 64
    PLAYER_FRAMES = 4  # ajuste conforme seu spritesheet
    player_textures = load_spritesheet('textures/player_anim.png', PLAYER_FRAME_W, PLAYER_FRAME_H, PLAYER_FRAMES)

    # --- Tiles quad/VAO (losango) ---
    quad, quad_idx = make_diamond_quad(tile_px_w, tile_px_h)
    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    EBO = glGenBuffers(1)
    glBindVertexArray(VAO)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, quad.nbytes, quad, GL_STATIC_DRAW)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, quad_idx.nbytes, quad_idx, GL_STATIC_DRAW)
    shader = compileProgram(
        compileShader(SPRITE_VERTEX_SHADER, GL_VERTEX_SHADER),
        compileShader(SPRITE_FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
    )
    pos_loc = glGetAttribLocation(shader, "position")
    tex_loc = glGetAttribLocation(shader, "texcoord")
    glEnableVertexAttribArray(pos_loc)
    glVertexAttribPointer(pos_loc, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(0))
    glEnableVertexAttribArray(tex_loc)
    glVertexAttribPointer(tex_loc, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(8))
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    # --- Player quad/VAO (retangular 64x64) ---
    player_quad, player_quad_idx = make_rect_quad(PLAYER_FRAME_W, PLAYER_FRAME_H)
    player_VAO = glGenVertexArrays(1)
    player_VBO = glGenBuffers(1)
    player_EBO = glGenBuffers(1)
    glBindVertexArray(player_VAO)
    glBindBuffer(GL_ARRAY_BUFFER, player_VBO)
    glBufferData(GL_ARRAY_BUFFER, player_quad.nbytes, player_quad, GL_STATIC_DRAW)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, player_EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, player_quad_idx.nbytes, player_quad_idx, GL_STATIC_DRAW)
    glEnableVertexAttribArray(pos_loc)
    glVertexAttribPointer(pos_loc, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(0))
    glEnableVertexAttribArray(tex_loc)
    glVertexAttribPointer(tex_loc, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(8))
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_TEXTURE_2D)

    MOVE_KEYS = {
        K_s:  (-1,  0),   # Baixo
        K_w:  ( 1,  0),   # Cima
        K_a:  ( 0, -1),   # Esquerda
        K_d:  ( 0,  1),   # Direita
        K_z:  (-1, -1),   # Baixo-Esquerda
        K_c:  (-1,  1),   # Baixo-Direita
        K_q:  ( 1, -1),   # Cima-Esquerda
        K_e:  ( 1,  1),   # Cima-Direita
    }

    (tilemap, player, vidas, game_over, venceu, last_safe_pos,
     couro_positions, couro_coletado, tem_bota, caminho_oculto, ciclo_passos, ciclo_idx) = reset_game()
    player.frame = 0

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                if not game_over and not venceu:
                    move = MOVE_KEYS.get(event.key)
                    if move:
                        dr, dc = move
                        new_row = player.row + dr
                        new_col = player.col + dc

                        if 0 <= new_row < tilemap.height and 0 <= new_col < tilemap.width:
                            tile = tilemap.tiles[new_row][new_col]
                            pegou_couro = (new_row, new_col) in couro_positions and (new_row, new_col) not in couro_coletado

                            if (new_row, new_col) != (player.row, player.col):
                                ciclo_idx = (ciclo_idx + 1) % len(ciclo_passos)
                                caminho_oculto = ciclo_passos[ciclo_idx]
                                player.frame = (player.frame + 1) % PLAYER_FRAMES

                            if tile == "lava":
                                if tem_bota:
                                    player.set_position(new_row, new_col)
                                    venceu = True
                                    print("Parabéns! Você coletou todos os couros, ganhou a bota e atravessou a lava. Você venceu o jogo!")
                                else:
                                    player.set_position(new_row, new_col)
                                    game_over = True
                                    print("Game Over! Você caiu na lava.")
                            elif tile == "pedra":
                                player.set_position(new_row, new_col)
                                last_safe_pos = (new_row, new_col)
                            elif tile == "preto":
                                vidas -= 1
                                print(f"Perdeu 1 vida! ({vidas} restantes)")
                                player.set_position(*last_safe_pos)
                                if vidas <= 0:
                                    game_over = True
                                    print("Game Over! Fim das vidas.")
                            else:
                                player.set_position(new_row, new_col)
                                last_safe_pos = (new_row, new_col)

                            if pegou_couro:
                                couro_coletado.add((new_row, new_col))
                                print(f"Pegou couro! ({len(couro_coletado)}/5)")
                                if len(couro_coletado) == 5 and not tem_bota:
                                    tem_bota = True
                                    print("Você ganhou a bota! Agora pode atravessar lava.")
                # Para recomeçar o jogo após o game over, pressione R
                if game_over and event.key == K_r:
                    (tilemap, player, vidas, game_over, venceu, last_safe_pos,
                     couro_positions, couro_coletado, tem_bota, caminho_oculto, ciclo_passos, ciclo_idx) = reset_game()
                    player.frame = 0
                    print("Jogo reiniciado!")

        glClearColor(0.08, 0.08, 0.08, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(shader)
        offset_loc = glGetUniformLocation(shader, "offset")
        scale_loc = glGetUniformLocation(shader, "scale")
        tex_uniform = glGetUniformLocation(shader, "tileTexture")
        glUniform1i(tex_uniform, 0) 

        # Tiles
        glBindVertexArray(VAO)
        tiles_sorted = sorted([(row, col) for row in range(tilemap.height) for col in range(tilemap.width)],
                              key=lambda rc: rc[0]+rc[1])
        for row, col in tiles_sorted:
            tiletype = tilemap.tiles[row][col]
            draw_tiletype = tiletype
            if tiletype == "pedra":
                if caminho_oculto and (row, col) != (player.row, player.col):
                    draw_tiletype = "preto"
            texid = tile_textures[draw_tiletype]
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, texid)
            px, py = iso_pos(row, col, tilemap.width, tilemap.height, tile_px_w, tile_px_h, screen_w, screen_h)
            glUniform2f(offset_loc, px, py)
            glUniform2f(scale_loc, 1.0 / (screen_w / 2), 1.0 / (screen_h / 2))
            glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
            glBindTexture(GL_TEXTURE_2D, 0)
        glBindVertexArray(0)

        # Couro
        glBindVertexArray(VAO)
        for (row, col) in couro_positions:
            if (row, col) not in couro_coletado:
                visivel = (not caminho_oculto)
                if tilemap.tiles[row][col] == "pedra" and visivel:
                    glActiveTexture(GL_TEXTURE0)
                    glBindTexture(GL_TEXTURE_2D, couro_texture)
                    px, py = iso_pos(row, col, tilemap.width, tilemap.height, tile_px_w, tile_px_h, screen_w, screen_h)
                    glUniform2f(offset_loc, px, py - 0.02)
                    glUniform2f(scale_loc, 0.5 * 1.0 / (screen_w / 2), 0.5 * 1.0 / (screen_h / 2))
                    glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
                    glBindTexture(GL_TEXTURE_2D, 0)
        glBindVertexArray(0)

        # Player
        glBindVertexArray(player_VAO)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, player_textures[player.frame])
        prow, pcol = player.row, player.col
        px, py = iso_pos(prow, pcol, tilemap.width, tilemap.height, tile_px_w, tile_px_h, screen_w, screen_h)
        glUniform2f(offset_loc, px, py)
        glUniform2f(scale_loc, 1.0 / (screen_w / 2), 1.0 / (screen_h / 2))
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
        glBindTexture(GL_TEXTURE_2D, 0)
        glBindVertexArray(0)

        # Overlay: vidas, couro, bota
        if not game_over and not venceu:
            draw_text(screen_surf, f"Vidas: {vidas}", (120, 40), (255,255,255), font_size=36, center=False)
            draw_text(screen_surf, f"Couro: {len(couro_coletado)}/5", (120, 80), (210,180,140), font_size=36, center=False)
            if tem_bota:
                draw_text(screen_surf, "BOTA: ATIVA", (120, 120), (0,255,0), font_size=36, center=False)
        elif venceu:
            draw_text(screen_surf, "VOCÊ VENCEU!", (screen_w // 2, screen_h // 2), (0,255,0), font_size=64)
        else:
            draw_text(screen_surf, "Game Over", (screen_w // 2, screen_h // 2), (255,0,0), font_size=64)
            draw_text(screen_surf, "Pressione R para recomeçar ou ESC para sair",
                      (screen_w // 2, screen_h // 2 + 80), (255,255,0), font_size=36)

        pygame.display.flip()

        if venceu:
            pygame.time.wait(2000)
            (tilemap, player, vidas, game_over, venceu, last_safe_pos,
             couro_positions, couro_coletado, tem_bota, caminho_oculto, ciclo_passos, ciclo_idx) = reset_game()
            player.frame = 0

        keys = pygame.key.get_pressed()
        if game_over and keys[K_ESCAPE]:
            running = False

        clock.tick(60)

    glDeleteBuffers(1, [VBO, EBO, player_VBO, player_EBO])
    glDeleteVertexArrays(1, [VAO, player_VAO])
    pygame.quit()

if __name__ == "__main__":
    main()