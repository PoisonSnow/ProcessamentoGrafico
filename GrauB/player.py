class Player:
    def __init__(self, row, col, sprite_path="textures/player.png"):
        self.row = row
        self.col = col
        self.sprite_path = sprite_path
        self._texture_id = None

    def set_position(self, row, col):
        self.row = row
        self.col = col

    def get_texture(self):
        return self._texture_id

    def load_texture(self, loader_func):
        self._texture_id = loader_func(self.sprite_path)