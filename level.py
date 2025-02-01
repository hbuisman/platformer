import pygame

BLUE = (0, 0, 255)
LILA = (200, 0, 200)  # new color for trampoline
ORANGE = (255, 165, 0)  # Portal entrance color
BLUE_PORTAL = (0, 191, 255)  # Portal exit color

class Portal:
    def __init__(self, x, y, is_entrance=True, portal_id=1):
        self.rect = pygame.Rect(x, y, 30, 60)  # Taller than wide
        self.is_entrance = is_entrance
        self.portal_id = portal_id
        self.font = pygame.font.SysFont(None, 24)
    
    def draw(self, surface, is_dragging=False):
        # Draw portal oval/rectangle
        color = ORANGE if self.is_entrance else BLUE_PORTAL
        if is_dragging:
            color = (255, 0, 255)  # magenta when dragging
        pygame.draw.ellipse(surface, color, self.rect)
        
        # Draw portal number
        text = self.font.render(str(self.portal_id), True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

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
        
        self.slides = [
            SlidePlatform(500, 350, 700, 550)
        ]
        self.portals = []  # Will store Portal objects
        self.next_portal_id = 1

        # For dragging logic:
        self.dragging_item = None  # Will hold a reference to whichever item (Rect or SlidePlatform) is being dragged
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        # Load and scale the original grass image so it is 50px tall (the ground platform's height)
        ground_texture_orig = pygame.image.load("images/grass-platform.png").convert_alpha()
        height_ratio = 50 / ground_texture_orig.get_height()
        scaled_w = int(ground_texture_orig.get_width() * height_ratio)
        scaled_h = 50
        self.ground_texture = pygame.transform.smoothscale(ground_texture_orig, (scaled_w, scaled_h))

        # Load stone texture for other platforms
        stone_texture_orig = pygame.image.load("images/stone-platform.png").convert_alpha()
        # Scale stone texture to match platform height (20px)
        height_ratio = 20 / stone_texture_orig.get_height()
        scaled_w = int(stone_texture_orig.get_width() * height_ratio)
        scaled_h = 20
        self.stone_texture = pygame.transform.smoothscale(stone_texture_orig, (scaled_w, scaled_h))

        # Load trampoline texture
        tramp_texture_orig = pygame.image.load("images/trampoline.png").convert_alpha()
        # Scale to match trampoline height (40px - twice as tall)
        height_ratio = 40 / tramp_texture_orig.get_height()
        scaled_w = int(tramp_texture_orig.get_width() * height_ratio)
        scaled_h = 40
        self.tramp_texture = pygame.transform.smoothscale(tramp_texture_orig, (scaled_w, scaled_h))
        # Calculate width maintaining aspect ratio of 363:198
        self.tramp_width = int(40 * (363/198))  # If height is 40, width should be ~73
        
        # Initialize trampolines after we have calculated tramp_width
        self.trampolines = [
            pygame.Rect(900, 580, self.tramp_width, 40)  # Correct aspect ratio
        ]

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
                    mouse_x, mouse_y = event.pos
                    clicked_item = self.find_clicked_item(mouse_x, mouse_y)
                    if clicked_item:
                        self.dragging_item = clicked_item
                        # Compute offset from top-left corner
                        if isinstance(clicked_item, Portal):
                            self.drag_offset_x = mouse_x - clicked_item.rect.x
                            self.drag_offset_y = mouse_y - clicked_item.rect.y
                        elif isinstance(clicked_item, pygame.Rect):
                            self.drag_offset_x = mouse_x - clicked_item.x
                            self.drag_offset_y = mouse_y - clicked_item.y
                        elif isinstance(clicked_item, SlidePlatform):
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
        for p in self.platforms[1:]:  # Start from second platform
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
        # Check portals
        for portal in self.portals:
            if portal.rect.collidepoint(mouse_x, mouse_y):
                return portal
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
        elif isinstance(self.dragging_item, Portal):
            self.dragging_item.rect.x = mouse_x - self.drag_offset_x
            self.dragging_item.rect.y = mouse_y - self.drag_offset_y

    def draw(self, surface):
        # Draw ground (first platform)
        ground = self.platforms[0]
        self.draw_ground_with_texture(surface, ground)

        # Draw other platforms
        for platform in self.platforms[1:]:
            if platform == self.dragging_item:
                # Draw highlighted platform when dragging
                pygame.draw.rect(surface, (255, 0, 255), platform, border_radius=3)
            else:
                # Draw stone texture
                self.draw_platform_with_texture(surface, platform)

        # Draw slides
        for slide in self.slides:
            if slide == self.dragging_item:
                slide.draw(surface, highlight=True)
            else:
                slide.draw(surface)

        # Draw trampolines
        for tramp in self.trampolines:
            if tramp == self.dragging_item:
                # Draw highlighted trampoline when dragging
                pygame.draw.rect(surface, (255, 0, 255), tramp, border_radius=3)
            else:
                # Draw trampoline texture
                self.draw_trampoline_with_texture(surface, tramp)

        # Draw portals
        for portal in self.portals:
            portal.draw(surface, portal == self.dragging_item)

    def draw_ground_with_texture(self, surface, ground):
        """Repeatedly blit the scaled grass texture on the ground platform."""
        texture_w = self.ground_texture.get_width()
        texture_h = self.ground_texture.get_height()
        for x in range(ground.x, ground.x + ground.width, texture_w):
            for y in range(ground.y, ground.y + ground.height, texture_h):
                surface.blit(self.ground_texture, (x, y))

    def draw_platform_with_texture(self, surface, platform):
        """Draw a non-ground platform using the stone texture."""
        texture_w = self.stone_texture.get_width()
        # Only need one row since platform height matches texture height
        for x in range(platform.x, platform.x + platform.width, texture_w):
            surface.blit(self.stone_texture, (x, platform.y))

    def draw_trampoline_with_texture(self, surface, tramp):
        """Draw a trampoline using the trampoline texture."""
        texture_w = self.tramp_texture.get_width()
        # Center the texture on the trampoline rect if sizes don't match
        x = tramp.x + (tramp.width - texture_w) // 2
        surface.blit(self.tramp_texture, (x, tramp.y))

    def remove_item(self, item):
        """Remove an existing platform, trampoline, or slide from the level."""
        if item in self.platforms:
            self.platforms.remove(item)
        elif item in self.trampolines:
            self.trampolines.remove(item)
        elif item in self.slides:
            self.slides.remove(item)
        elif item in self.portals:
            # Remove both entrance and exit of the pair
            portal_id = item.portal_id
            self.portals = [p for p in self.portals 
                          if p.portal_id != portal_id]
        if self.dragging_item == item:
            self.dragging_item = None

    def add_platform(self, x, y):
        # Create a new platform at the mouse position
        new_rect = pygame.Rect(x - 75, y - 10, 150, 20)  # Center on mouse
        self.platforms.append(new_rect)

    def add_slide(self, x, y):
        # Create a new Slide at mouse position, angled down-right
        new_slide = SlidePlatform(x, y, x + 100, y + 100)
        self.slides.append(new_slide)

    def add_trampoline(self, x, y):
        # Create a new trampoline at mouse position
        new_tramp = pygame.Rect(x - self.tramp_width//2, y - 20, self.tramp_width, 40)
        self.trampolines.append(new_tramp)

    def add_portal(self, x, y):
        """Add a new portal pair (entrance and exit)"""
        # Create entrance at mouse position
        entrance = Portal(x - 15, y - 30, is_entrance=True, portal_id=self.next_portal_id)
        # Create exit slightly offset to the right
        exit_portal = Portal(x + 50, y - 30, is_entrance=False, portal_id=self.next_portal_id)
        
        self.portals.extend([entrance, exit_portal])
        self.next_portal_id += 1

    def find_portal_pair(self, portal):
        """Find the other portal in a pair"""
        for p in self.portals:
            if (p.portal_id == portal.portal_id and 
                p.is_entrance != portal.is_entrance):
                return p
        return None

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