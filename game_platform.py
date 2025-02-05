import pygame

class Platform:
    def __init__(self, x, y, width, height, texture, tile_vertical=False):
        """
        Create a platform.

        Args:
            x, y: Top‐left coordinates.
            width, height: Dimensions of the platform.
            texture: A pre‐loaded pygame.Surface to be tiled.
            tile_vertical: If True, tile both horizontally and vertically.
                           (For the ground.) If False, tile only horizontally.
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.texture = texture
        self.tile_vertical = tile_vertical

    def draw(self, surface):
        """Draw the platform by tiling its texture."""
        if self.tile_vertical:
            texture_w = self.texture.get_width()
            texture_h = self.texture.get_height()
            for x in range(self.rect.x, self.rect.x + self.rect.width, texture_w):
                for y in range(self.rect.y, self.rect.y + self.rect.height, texture_h):
                    surface.blit(self.texture, (x, y))
        else:
            texture_w = self.texture.get_width()
            for x in range(self.rect.x, self.rect.x + self.rect.width, texture_w):
                surface.blit(self.texture, (x, self.rect.y))

    def draw_tinted(self, surface, tint_color):
        """
        Draw a tinted version of the platform.
        
        Args:
            surface: The pygame.Surface to draw on.
            tint_color: A (R,G,B,A) tuple used for the tint (e.g. (255,0,255,128)).
        """
        tinted_texture = self.texture.copy()
        overlay = pygame.Surface(tinted_texture.get_size(), pygame.SRCALPHA)
        overlay.fill(tint_color)
        tinted_texture.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        if self.tile_vertical:
            texture_w = tinted_texture.get_width()
            texture_h = tinted_texture.get_height()
            for x in range(self.rect.x, self.rect.x + self.rect.width, texture_w):
                for y in range(self.rect.y, self.rect.y + self.rect.height, texture_h):
                    surface.blit(tinted_texture, (x, y))
        else:
            texture_w = tinted_texture.get_width()
            for x in range(self.rect.x, self.rect.x + self.rect.width, texture_w):
                surface.blit(tinted_texture, (x, self.rect.y))

    def __getattr__(self, attr):
        # Delegate attribute lookup to the underlying rect so that properties
        # such as .top, .bottom, etc. work.
        return getattr(self.rect, attr)


class Ground(Platform):
    DEFAULT_IMAGE_PATH = "images/grass-platform.png"
    DEFAULT_HEIGHT = 50

    def __init__(self, x, y, width, height=None):
        """
        Ground platforms tile their texture both horizontally and vertically.
        If height is not provided, it defaults to DEFAULT_HEIGHT.
        """
        if height is None:
            height = Ground.DEFAULT_HEIGHT
        # Load and scale the ground texture to have the desired height while preserving aspect ratio.
        original = pygame.image.load(Ground.DEFAULT_IMAGE_PATH).convert_alpha()
        ratio = height / original.get_height()
        new_width = int(original.get_width() * ratio)
        texture = pygame.transform.smoothscale(original, (new_width, height))
        super().__init__(x, y, width, height, texture, tile_vertical=True)


class StonePlatform(Platform):
    DEFAULT_IMAGE_PATH = "images/stone-platform.png"

    def __init__(self, x, y, width, height):
        """
        Stone platforms tile their texture only horizontally.
        """
        # Load and scale the stone texture so that its height matches the desired platform height.
        original = pygame.image.load(StonePlatform.DEFAULT_IMAGE_PATH).convert_alpha()
        ratio = height / original.get_height()
        new_width = int(original.get_width() * ratio)
        texture = pygame.transform.smoothscale(original, (new_width, height))
        super().__init__(x, y, width, height, texture, tile_vertical=False)
