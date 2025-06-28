from OpenGL.GL import *
import numpy as np

def create_tile_vao(tile_width, tile_height):
    # Vértices (x, y) do losango isométrico centrado na origem
    vertices = np.array([
        [0, -tile_height // 2],              # Top
        [tile_width // 2, 0],                # Right
        [0, tile_height // 2],               # Bottom
        [-tile_width // 2, 0],               # Left
    ], dtype=np.float32)

    # Coordenadas de textura (u, v) para cada vértice
    texcoords = np.array([
        [0.5, 0.0],      # Top
        [1.0, 0.5],      # Right
        [0.5, 1.0],      # Bottom
        [0.0, 0.5],      # Left
    ], dtype=np.float32)

    # Índices para dois triângulos que formam o losango
    indices = np.array([
        0, 1, 2,
        0, 2, 3
    ], dtype=np.uint32)

    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # VBO de vértices
    vbo_vertices = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_vertices)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(2, GL_FLOAT, 0, None)

    # VBO de coordenadas de textura
    vbo_texcoords = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_texcoords)
    glBufferData(GL_ARRAY_BUFFER, texcoords.nbytes, texcoords, GL_STATIC_DRAW)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)
    glTexCoordPointer(2, GL_FLOAT, 0, None)

    ibo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    return vao, vbo_vertices, vbo_texcoords, ibo