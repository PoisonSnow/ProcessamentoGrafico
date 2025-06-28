import random
from player import Player

class TileMap:
    def __init__(self, tiles, player=None):
        self.tiles = tiles
        self.height = len(tiles)
        self.width = len(tiles[0]) if tiles else 0
        self.player = player

    @classmethod
    def generate_varied_branching_paths(
        cls, width=15, height=15, player_sprite="textures/player.png"
    ):
        tiles = [["preto" for _ in range(width)] for _ in range(height)]

        # Caminho principal 
        start_col = random.randint(2, width-3)
        curr_col = start_col
        main_path = [(0, curr_col)]
        for r in range(1, 7):
            options = [curr_col]
            if curr_col > 1: options.append(curr_col-1)
            if curr_col < width-2: options.append(curr_col+1)
            curr_col = random.choice(options)
            main_path.append((r, curr_col))

        bif_col = curr_col

        # Caminho 1 
        c1_col = bif_col
        c1_path = []
        for r in range(7, 14):
            options = [c1_col]
            if c1_col > 1: options.append(c1_col-1)
            if c1_col < width-2: options.append(c1_col+1)
            weights = [3 if o == c1_col else 1 for o in options]
            c1_col = random.choices(options, weights=weights)[0]
            c1_path.append((r, c1_col))

        # Caminho 2 
        c2_row, c2_col = 6, bif_col
        c2_path = []
        if c1_col > bif_col:
            far_col = max(1, bif_col - 4)
        else:
            far_col = min(width-2, bif_col + 4)
        for r in range(7, 10):
            if c2_col < far_col: c2_col += 1
            elif c2_col > far_col: c2_col -= 1
            c2_path.append((r, c2_col))
        for r in range(10, 13):
            options = [c2_col]
            if c2_col > 1: options.append(c2_col-1)
            if c2_col < width-2: options.append(c2_col+1)
            options = [o for o in options if abs(o - c1_col) >= 2]
            if not options:
                options = [c2_col]
            c2_col = random.choice(options)
            c2_path.append((r, c2_col))
        final_col = c1_path[-1][1]
        while c2_col != final_col:
            if c2_col < final_col: c2_col += 1
            elif c2_col > final_col: c2_col -= 1
            c2_path.append((13, c2_col))
        if (13, final_col) not in c2_path:
            c2_path.append((13, final_col))

        for r, c in main_path:
            tiles[r][c] = "pedra"
        for r, c in c1_path:
            tiles[r][c] = "pedra"
        for r, c in c2_path:
            tiles[r][c] = "pedra"
        for c in range(width):
            tiles[14][c] = "lava"

        player = Player(0, main_path[0][1], sprite_path=player_sprite)
        return cls(tiles, player=player)

    def draw(self, screen, tile_size, tile_images):
        """
        Desenha o tilemap na tela usando pygame.
        :param screen: superfície pygame onde desenhar
        :param tile_size: tamanho do tile em pixels
        :param tile_images: dict {'preto': pygame.Surface, 'pedra': pygame.Surface, 'lava': pygame.Surface}
        """
        import pygame

        for row in range(self.height):
            for col in range(self.width):
                tile = self.tiles[row][col]
                img = tile_images[tile]
                screen.blit(img, (col * tile_size, row * tile_size))

        # Desenha o player
        if self.player:
            player_img = pygame.image.load(self.player.sprite_path).convert_alpha()
            player_img = pygame.transform.scale(player_img, (tile_size, tile_size))
            screen.blit(player_img, (self.player.col * tile_size, self.player.row * tile_size))

    def draw_opengl(self, tile_size, textures):
        """
        Desenha o tilemap usando OpenGL (PyOpenGL).
        :param tile_size: tamanho do tile em pixels
        :param textures: dict {'preto': texture_id, 'pedra': texture_id, 'lava': texture_id, 'player': texture_id}
        """
        from OpenGL.GL import glBindTexture, glBegin, glEnd, glTexCoord2f, glVertex2f, GL_QUADS, GL_TEXTURE_2D

        for row in range(self.height):
            for col in range(self.width):
                tile = self.tiles[row][col]
                tex_id = textures[tile]
                glBindTexture(GL_TEXTURE_2D, tex_id)
                x = col * tile_size
                y = row * tile_size
                glBegin(GL_QUADS)
                glTexCoord2f(0, 0)
                glVertex2f(x, y)
                glTexCoord2f(1, 0)
                glVertex2f(x + tile_size, y)
                glTexCoord2f(1, 1)
                glVertex2f(x + tile_size, y + tile_size)
                glTexCoord2f(0, 1)
                glVertex2f(x, y + tile_size)
                glEnd()

        # Player
        if self.player:
            tex_id = textures.get("player")
            if tex_id is not None:
                col = self.player.col
                row = self.player.row
                x = col * tile_size
                y = row * tile_size
                glBindTexture(GL_TEXTURE_2D, tex_id)
                glBegin(GL_QUADS)
                glTexCoord2f(0, 0)
                glVertex2f(x, y)
                glTexCoord2f(1, 0)
                glVertex2f(x + tile_size, y)
                glTexCoord2f(1, 1)
                glVertex2f(x + tile_size, y + tile_size)
                glTexCoord2f(0, 1)
                glVertex2f(x, y + tile_size)
                glEnd()