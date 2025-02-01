import pygame

# Mouse cursors
DEFAULT_CURSOR = pygame.SYSTEM_CURSOR_ARROW
HAND_CURSOR = pygame.SYSTEM_CURSOR_HAND

# Represent each inventory "icon" as a small box
# We'll store "type", "color", and a rect relative to the panel
ICONS = [
    {"type": "platform",   "color": (0, 0, 255),   "rect": pygame.Rect(10,  50, 40, 40)},
    {"type": "slide",      "color": (0, 200, 0),   "rect": pygame.Rect(10, 110, 40, 40)},
    {"type": "trampoline", "color": (200, 0, 200), "rect": pygame.Rect(10, 170, 40, 40)},
    {"type": "portal",     "color": (255, 165, 0), "rect": pygame.Rect(10, 230, 40, 40)},
]

# Colors for character selection buttons
BUTTON_BORDER_COLOR = (100, 100, 100)  # Normal border color
BUTTON_HOVER_COLOR = (255, 255, 255)   # Border color when hovering
BUTTON_BORDER_WIDTH = 2

# Character selection portraits
PORTRAIT_SIZE = 60
CHARACTERS = [
    {
        "id": "big",
        "portrait": pygame.image.load("images/player_big_portrait.png"),
        "sprite": "images/player_big.png",
        "sound": "sounds/big_player_ouch.wav",
        "rect": pygame.Rect(10, 650, PORTRAIT_SIZE, PORTRAIT_SIZE),
        "hovered": False
    },
    {
        "id": "small",
        "portrait": pygame.image.load("images/player_small_portrait.png"),
        "sprite": "images/player_small.png",
        "sound": "sounds/small_player_ouch.wav",
        "rect": pygame.Rect(80, 650, PORTRAIT_SIZE, PORTRAIT_SIZE),
        "hovered": False
    }
]

class InventoryPanel:
    def __init__(self, screen_width, screen_height):
        self.width = 200
        self.height = screen_height
        self.x = screen_width  # start fully hidden off the right edge
        self.goal_x = screen_width
        self.open = False

        # Keep track of the icon currently being dragged (None if none)
        self.dragging_icon = None

        # Scale portrait images
        for char in CHARACTERS:
            char["portrait"] = pygame.transform.scale(char["portrait"], 
                                                    (PORTRAIT_SIZE, PORTRAIT_SIZE))

    def toggle(self, screen_width):
        self.open = not self.open
        if self.open:
            self.goal_x = screen_width - self.width
        else:
            self.goal_x = screen_width

    def update_character_hover_states(self, mouse_pos):
        """Update hover states and cursor based on mouse position"""
        mx, my = mouse_pos
        is_hovering_any = False
        
        for char in CHARACTERS:
            rect_copy = char["rect"].copy()
            rect_copy.x += self.x
            char["hovered"] = self.open and rect_copy.collidepoint(mx, my)
            if char["hovered"]:
                is_hovering_any = True
        
        # Set appropriate cursor
        if is_hovering_any:
            pygame.mouse.set_cursor(HAND_CURSOR)
        else:
            pygame.mouse.set_cursor(DEFAULT_CURSOR)

    def update(self):
        # Animate panel sliding in/out
        if self.x < self.goal_x:
            self.x += min(10, self.goal_x - self.x)
        elif self.x > self.goal_x:
            self.x -= min(10, self.x - self.goal_x)
        
        # Update hover states
        if self.open:
            self.update_character_hover_states(pygame.mouse.get_pos())

    def draw(self, surface):
        # Create a surface to draw the semi-transparent panel
        panel_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Fill with a semi-transparent gray (RGBA)
        # 160,160,160 is the gray color; 180 alpha = ~70% opacity
        panel_surf.fill((160, 160, 160, 180))

        # Draw a vertical black border line on the left side
        border_x = 0
        pygame.draw.line(panel_surf, (0, 0, 0), (border_x, 0), (border_x, self.height), 2)

        # Optionally, add a simple drop shadow effect on the left:
        # We'll create a small gradient from black to transparent, a few pixels wide.
        shadow_width = 8
        for i in range(shadow_width):
            alpha = int(100 * (1 - i / shadow_width))  # fades from 100 -> 0
            pygame.draw.line(
                panel_surf, 
                (0, 0, 0, alpha), 
                (border_x - (i + 1), 0), 
                (border_x - (i + 1), self.height), 
                1
            )

        # Now blit this panel_surf onto the main surface at (self.x, 0)
        surface.blit(panel_surf, (self.x, 0))
        
        # Draw inventory icons (colored boxes)
        for icon in ICONS:
            rect_copy = icon["rect"].copy()
            rect_copy.x += self.x
            pygame.draw.rect(surface, icon["color"], rect_copy)
        
        # Draw character portraits with borders
        for char in CHARACTERS:
            rect_copy = char["rect"].copy()
            rect_copy.x += self.x
            
            # Draw border (color changes based on hover state)
            border_color = BUTTON_HOVER_COLOR if char["hovered"] else BUTTON_BORDER_COLOR
            pygame.draw.rect(surface, border_color, rect_copy, BUTTON_BORDER_WIDTH)
            
            # Draw portrait inside border
            surface.blit(char["portrait"], rect_copy)
        
        # If we are dragging an icon, draw a ghost of it at the current mouse position
        if self.dragging_icon:
            mx, my = pygame.mouse.get_pos()
            w = self.dragging_icon["rect"].width
            h = self.dragging_icon["rect"].height
            color = self.dragging_icon["color"]
            # Center the drag icon on the mouse
            draw_rect = pygame.Rect(mx - w//2, my - h//2, w, h)
            pygame.draw.rect(surface, color, draw_rect, border_radius=5)

    def handle_event(self, event, level, player):
        # Only process if we are open
        if not self.open:
            pygame.mouse.set_cursor(DEFAULT_CURSOR)
            return
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check for character selection clicks
            for char in CHARACTERS:
                rect_copy = char["rect"].copy()
                rect_copy.x += self.x
                if rect_copy.collidepoint(event.pos):
                    player.change_character(char["sprite"], char["sound"])
                    pygame.mouse.set_cursor(DEFAULT_CURSOR)
                    return
            
            # Check if clicked on any icon in the panel
            mx, my = event.pos
            for icon in ICONS:
                # Calc absolute rect on screen
                abs_rect = icon["rect"].copy()
                abs_rect.x += self.x
                if abs_rect.collidepoint(mx, my):
                    self.dragging_icon = icon
                    break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging_icon:
                # If we released outside the panel, add item to the level
                mx, my = event.pos
                panel_rect = pygame.Rect(self.x, 0, self.width, self.height)
                if not panel_rect.collidepoint(mx, my):
                    if self.dragging_icon["type"] == "platform":
                        level.add_platform(mx, my)
                    elif self.dragging_icon["type"] == "slide":
                        level.add_slide(mx, my)
                    elif self.dragging_icon["type"] == "trampoline":
                        level.add_trampoline(mx, my)
                    elif self.dragging_icon["type"] == "portal":
                        level.add_portal(mx, my)
                # End drag
                self.dragging_icon = None 