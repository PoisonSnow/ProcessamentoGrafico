import pygame
from OpenGL.GL import *

def load_texture(filename):
    """
    Carrega uma imagem e retorna o ID da textura OpenGL.
    """
    surf = pygame.image.load(filename)
    image = pygame.image.tostring(surf, "RGBA", True)
    width, height = surf.get_rect().size

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)

    glBindTexture(GL_TEXTURE_2D, 0)
    return texture_id