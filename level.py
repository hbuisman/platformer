import pygame

BLUE = (0, 0, 255)
LILA = (200, 0, 200)  # new color for trampoline

class Level:
    def __init__(self):
        # You can define platforms here or load them from a file, etc.
        self.platforms = [
            pygame.Rect(0, 750, 1200, 50),   # Floor (for 800px high window)
            pygame.Rect(300, 600, 150, 20),  # Lower platform
            pygame.Rect(500, 500, 150, 20),  # Middle platform
            pygame.Rect(700, 450, 150, 20),  # Another one for vertical stepping
            pygame.Rect(900, 400, 150, 20),  # A bit higher
        ]
        
        # ADD A DIAGONAL SLIDE PLATFORM HERE:
        self.slides = [
            # This slide goes from (500, 250) down to (700, 550)
            # Adjust coordinates however you like
            SlidePlatform(500, 350, 700, 550)
        ]
        # Move trampoline to a better location (x=900, y=600)
        self.trampolines = [
            pygame.Rect(900, 600, 75, 20)
        ]

        # For dragging logic:
        self.dragging_item = None  # Will hold a reference to whichever item (Rect or SlidePlatform) is being dragged
        self.drag_offset_x = 0
        self.drag_offset_y = 0

    def handle_mouse_events(self, events):
        """Give this method a list of pygame events. Handles click-dragging of items."""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:  # right-click -> remove item if clicked
                    mouse_x, mouse_y = event.pos
                    item = self.find_clicked_item(mouse_x, mouse_y)
                    if item:
                        self.remove_item(item)
                        continue
                if event.button == 1:
                    # Left-click: see if we clicked on a platform, slide, or trampoline
                    mouse_x, mouse_y = event.pos
                    clicked_item = self.find_clicked_item(mouse_x, mouse_y)
                    if clicked_item:
                        self.dragging_item = clicked_item
                        # Compute offset from top-left corner (or from the line start for a SlidePlatform)
                        if isinstance(clicked_item, pygame.Rect):
                            self.drag_offset_x = mouse_x - clicked_item.x
                            self.drag_offset_y = mouse_y - clicked_item.y
                        else:
                            # SlidePlatform: store offset from x1,y1
                            self.drag_offset_x = mouse_x - clicked_item.x1
                            self.drag_offset_y = mouse_y - clicked_item.y1

            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_item:
                    mouse_x, mouse_y = event.pos
                    self.drag_item_to(mouse_x, mouse_y)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                # Stop dragging
                self.dragging_item = None

    def find_clicked_item(self, mouse_x, mouse_y):
        """Check if mouse_x, mouse_y is inside a Rect or near a SlidePlatform."""
        # First check each platform
        for p in self.platforms:
            if p.collidepoint(mouse_x, mouse_y):
                return p
        # Then check trampolines
        for t in self.trampolines:
            if t.collidepoint(mouse_x, mouse_y):
                return t
        # Check slides (treat them as lines, see if mouse is close)
        for s in self.slides:
            if s.point_is_near(mouse_x, mouse_y, threshold=8):
                return s
        return None

    def drag_item_to(self, mouse_x, mouse_y):
        """Given a mouse position, move the currently dragged item to that position."""
        if isinstance(self.dragging_item, pygame.Rect):
            # Move rect so the top-left follows the mouse offset
            self.dragging_item.x = mouse_x - self.drag_offset_x
            self.dragging_item.y = mouse_y - self.drag_offset_y
        elif isinstance(self.dragging_item, SlidePlatform):
            # Move the line by offset
            dx = (mouse_x - self.drag_offset_x) - self.dragging_item.x1
            dy = (mouse_y - self.drag_offset_y) - self.dragging_item.y1
            self.dragging_item.x1 += dx
            self.dragging_item.y1 += dy
            self.dragging_item.x2 += dx
            self.dragging_item.y2 += dy

    def draw(self, surface):
        for platform in self.platforms:
            if platform == self.dragging_item:
                # Show platform in a different color while dragging
                pygame.draw.rect(surface, (255, 0, 255), platform)  # magenta
            else:
                pygame.draw.rect(surface, BLUE, platform)
        # Draw the slide(s)
        for slide in self.slides:
            if slide == self.dragging_item:
                slide.draw(surface, highlight=True)
            else:
                slide.draw(surface)
        # Draw trampolines in LILA
        for tramp in self.trampolines:
            if tramp == self.dragging_item:
                pygame.draw.rect(surface, (255, 0, 255), tramp)
            else:
                pygame.draw.rect(surface, LILA, tramp)

    def remove_item(self, item):
        """Remove an existing platform, trampoline, or slide from the level."""
        if item in self.platforms:
            self.platforms.remove(item)
        elif item in self.trampolines:
            self.trampolines.remove(item)
        elif item in self.slides:
            self.slides.remove(item)
        if self.dragging_item == item:
            self.dragging_item = None

    def add_platform(self):
        # Create a new platform near the top left, for example
        new_rect = pygame.Rect(50, 50, 150, 20)
        self.platforms.append(new_rect)

    def add_slide(self):
        # Create a new Slide from (100,100) to (200,200)
        new_slide = SlidePlatform(100, 100, 200, 200)
        self.slides.append(new_slide)

    def add_trampoline(self):
        # Create a new trampoline near the top left
        new_tramp = pygame.Rect(100, 150, 75, 20)
        self.trampolines.append(new_tramp)

class SlidePlatform:
    def __init__(self, x1, y1, x2, y2):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.color = (0, 200, 0)  # green line for the slide

    def draw(self, surface, highlight=False):
        color = self.color
        if highlight:
            color = (255, 0, 255)  # magenta if being dragged
        pygame.draw.line(surface, color, (self.x1, self.y1), (self.x2, self.y2), 5)

    def point_is_near(self, mx, my, threshold=8):
        """Check if point (mx,my) is within 'threshold' distance of the line segment."""
        # We'll do a simple distance-from-segment check:
        # Formula ref: https://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment
        import math
        px, py = mx, my
        ax, ay = self.x1, self.y1
        bx, by = self.x2, self.y2
        # Vector from A->B
        abx = bx - ax
        aby = by - ay
        # Vector from A->P
        apx = px - ax
        apy = py - ay

        ab_len_sq = abx**2 + aby**2
        if ab_len_sq == 0:
            # Degenerate line
            dist_sq = (px - ax)**2 + (py - ay)**2
            return dist_sq <= threshold**2

        # Dot product, clamp [0,1]
        t = (apx * abx + apy * aby) / float(ab_len_sq)
        if t < 0:
            t = 0
        elif t > 1:
            t = 1

        # Projection
        projx = ax + t * abx
        projy = ay + t * aby

        # Distance from P to the projection
        dist_sq = (px - projx)**2 + (py - projy)**2
        return dist_sq <= threshold**2 