class Draggable:
    def start_drag(self, mouse_x, mouse_y):
        """Record the offset between the object's position and the mouse position.
        Assumes the object has a 'rect' attribute."""
        self.drag_offset_x = self.rect.x - mouse_x
        self.drag_offset_y = self.rect.y - mouse_y

    def update_drag(self, mouse_x, mouse_y):
        """Update the object's position based on the mouse position and stored offset."""
        self.rect.x = mouse_x + self.drag_offset_x
        self.rect.y = mouse_y + self.drag_offset_y
