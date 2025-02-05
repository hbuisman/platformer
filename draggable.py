import pygame

class Draggable:
    def __init__(self):
        self.being_dragged = False

    def start_drag(self, mouse_x, mouse_y):
        """Record the offset between the object’s position and the mouse position and mark it as being dragged."""
        self.drag_offset_x = self.rect.x - mouse_x
        self.drag_offset_y = self.rect.y - mouse_y
        self.being_dragged = True

    def update_drag(self, mouse_x, mouse_y):
        """Update the object’s position based on the mouse position and stored offset."""
        self.rect.x = mouse_x + self.drag_offset_x
        self.rect.y = mouse_y + self.drag_offset_y

    def end_drag(self):
        """Mark the object as no longer being dragged."""
        self.being_dragged = False

    def get_tinted_surface(self, surface, tint_color=(255, 0, 255, 128)):
        """Return a tinted copy of the given surface."""
        tinted = surface.copy()
        overlay = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
        overlay.fill(tint_color)
        tinted.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return tinted
