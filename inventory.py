import pygame

# Mouse cursors
DEFAULT_CURSOR = pygame.SYSTEM_CURSOR_ARROW
HAND_CURSOR = pygame.SYSTEM_CURSOR_HAND

# Represent each inventory "icon" as a small box
# We'll store "type", "color", and a rect relative to the panel
ICONS = [
    {
        "type": "platform",
        "color": (0, 0, 255),  # keep color as fallback
        "rect": pygame.Rect(10, 50, 225, 30),  # 1.5x larger
        "image_path": "images/stone-platform.png"
    },
    {
        "type": "slide",
        "color": (0, 200, 0),
        "rect": pygame.Rect(10, 110, 100, 92),  # Maintain 379:349 ratio
        "image_path": "images/slide.png"  # Add image path for slide
    },
    {
        "type": "trampoline",
        "color": (200, 0, 200),
        "rect": pygame.Rect(10, 230, 73, 40),  # match trampoline dimensions from level.py
        "image_path": "images/trampoline.png"
    },
    {
        "type": "portal",
        "color": (255, 165, 0),
        "rect": pygame.Rect(10, 290, 60, 120),  # match portal dimensions
        "image_path": "images/portal_entry.png"
    },
    {
        "type": "enemy1",
        "color": (255, 0, 0),  # Red for enemy
        "rect": pygame.Rect(10, 430, 60, 60),
        "image_path": "images/enemy1.png"
    },
    {
        "type": "enemy2", 
        "color": (255, 100, 0),  # Orange for enemy2
        "rect": pygame.Rect(10, 510, 60, 60),
        "image_path": "images/enemy2.png"
    },
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

# Add metadata for tooltips
ITEM_META = {
    "platform": {
        "name": "Stone Platform",
        "description": "A sturdy stone platform for steady footing.",
    },
    "slide": {
        "name": "Slide Platform",
        "description": "Slide down to have more fun!",
    },
    "trampoline": {
        "name": "Trampoline",
        "description": "Bounce into the air and reach higher places.",
    },
    "portal": {
        "name": "Portal",
        "description": "Instantly travel between two linked points.",
    },
    "enemy1": {
        "name": "Enemy Type 1",
        "description": "A basic enemy that causes damage on contact.",
    },
    "enemy2": {
        "name": "Enemy Type 2", 
        "description": "Another type of enemy to avoid.",
    },
}

class InventoryPanel:
    def __init__(self, screen_width, screen_height):
        self.width = 200
        self.height = screen_height
        self.x = screen_width  # start fully hidden off the right edge
        self.goal_x = screen_width
        self.open = False

        # Keep track of the icon currently being dragged (None if none)
        self.dragging_icon = None

        # Track which icon is hovered
        self.hovered_icon = None

        # Scale portrait images
        for char in CHARACTERS:
            char["portrait"] = pygame.transform.smoothscale(char["portrait"], 
                                                          (PORTRAIT_SIZE, PORTRAIT_SIZE))

        # Load and scale textures for inventory icons
        self.textures = {}
        for icon in ICONS:
            if "image_path" in icon:  # Only load if image_path exists
                if icon["type"] == "platform":
                    # Load original texture
                    original = pygame.image.load(icon["image_path"]).convert_alpha()
                    # Scale height to match platform height (20px)
                    height_ratio = 20 / original.get_height()
                    block_width = int(original.get_width() * height_ratio)
                    block_height = 20
                    scaled_block = pygame.transform.smoothscale(original, (block_width, block_height))
                    
                    # Create surface for the full platform width
                    platform_surface = pygame.Surface((icon["rect"].width, block_height), pygame.SRCALPHA)
                    # Tile the block texture horizontally
                    for x in range(0, icon["rect"].width, block_width):
                        platform_surface.blit(scaled_block, (x, 0))
                    self.textures[icon["type"]] = platform_surface
                else:
                    # Handle other textures normally
                    original = pygame.image.load(icon["image_path"]).convert_alpha()
                    scaled = pygame.transform.smoothscale(
                        original, 
                        (icon["rect"].width, icon["rect"].height)
                    )
                    self.textures[icon["type"]] = scaled

        # Center each icon horizontally in the panel
        for icon in ICONS:
            old_y = icon["rect"].y
            icon["rect"].x = (self.width - icon["rect"].width) // 2
            icon["rect"].y = old_y

    def toggle(self, screen_width):
        self.open = not self.open
        if self.open:
            self.goal_x = screen_width - self.width
        else:
            self.goal_x = screen_width

    def update_icon_hover_states(self, mouse_pos):
        """Check if the mouse is hovering any icon (not dragged)."""
        if not self.dragging_icon:
            self.hovered_icon = None
            panel_rect = pygame.Rect(self.x, 0, self.width, self.height)
            if panel_rect.collidepoint(*mouse_pos):
                for icon in ICONS:
                    abs_rect = icon["rect"].copy()
                    abs_rect.x += self.x
                    if abs_rect.collidepoint(mouse_pos):
                        self.hovered_icon = icon
                        break

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
        # Animate panel sliding in/out more quickly
        step = 15
        if self.x < self.goal_x:
            self.x += min(step, self.goal_x - self.x)
        elif self.x > self.goal_x:
            self.x -= min(step, self.x - self.goal_x)
        
        # Update hover states for icons & characters
        if self.open:
            mouse_pos = pygame.mouse.get_pos()
            self.update_icon_hover_states(mouse_pos)
            self.update_character_hover_states(mouse_pos)

    def draw_tooltip(self, surface, mouse_pos):
        """Draw a tooltip with item name/description if hovered."""
        if not self.hovered_icon:
            return
        item_type = self.hovered_icon["type"]
        meta = ITEM_META.get(item_type, {})
        if "name" not in meta:
            return
        name_txt = meta["name"]
        desc_txt = meta.get("description", "")
        
        # Create surfaces for text
        font = pygame.font.SysFont(None, 24)
        name_surf = font.render(name_txt, True, (255, 255, 255))
        desc_surf = font.render(desc_txt, True, (200, 200, 200))
        
        # Decide tooltip size
        padding = 8
        width = max(name_surf.get_width(), desc_surf.get_width()) + 2*padding
        height = name_surf.get_height() + desc_surf.get_height() + 3*padding
        
        # Place tooltip to the left of the mouse cursor, with small vertical offset
        tooltip_rect = pygame.Rect(0, 0, width, height)
        tooltip_rect.right = mouse_pos[0] - 16
        tooltip_rect.top = mouse_pos[1] + 16
        
        # Clamp tooltip so it doesn't go offscreen
        screen_w, screen_h = surface.get_size()
        if tooltip_rect.left < 0:
            tooltip_rect.left = 0
        if tooltip_rect.top < 0:
            tooltip_rect.top = 0
        if tooltip_rect.right > screen_w:
            tooltip_rect.right = screen_w
        if tooltip_rect.bottom > screen_h:
            tooltip_rect.bottom = screen_h
        
        pygame.draw.rect(surface, (40, 40, 40), tooltip_rect, border_radius=5)
        pygame.draw.rect(surface, (180, 180, 180), tooltip_rect, 1, border_radius=5)
        
        surface.blit(name_surf, (tooltip_rect.x + padding, tooltip_rect.y + padding))
        surface.blit(desc_surf, (tooltip_rect.x + padding, 
                                 tooltip_rect.y + padding + name_surf.get_height()))

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
        
        # Draw inventory icons
        for icon in ICONS:
            rect_copy = icon["rect"].copy()
            rect_copy.x += self.x
            
            if icon == self.hovered_icon and not self.dragging_icon:
                # Use the same magenta hue as with drag for consistent UX
                hover_texture = self.textures[icon["type"]].copy()
                overlay = pygame.Surface(hover_texture.get_size(), pygame.SRCALPHA)
                overlay.fill((255, 0, 255, 128))  # semi-transparent magenta
                hover_texture.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                surface.blit(hover_texture, rect_copy)
            else:
                # Draw normal texture
                surface.blit(self.textures[icon["type"]], rect_copy)
            
            # Remove border – no more pygame.draw.rect(...) around icons

        # Draw character portraits with borders
        for char in CHARACTERS:
            rect_copy = char["rect"].copy()
            rect_copy.x += self.x
            
            # Draw border (color changes based on hover state)
            border_color = BUTTON_HOVER_COLOR if char["hovered"] else BUTTON_BORDER_COLOR
            pygame.draw.rect(surface, border_color, rect_copy, BUTTON_BORDER_WIDTH)
            
            # Draw portrait inside border
            surface.blit(char["portrait"], rect_copy)
        
        # If dragging, update ghost drawing for slides too
        if self.dragging_icon:
            mx, my = pygame.mouse.get_pos()
            w = self.dragging_icon["rect"].width
            h = self.dragging_icon["rect"].height
            draw_rect = pygame.Rect(mx - w//2, my - h//2, w, h)
            
            # Create magenta-tinted version of texture for all items
            ghost_texture = self.textures[self.dragging_icon["type"]].copy()
            overlay = pygame.Surface(ghost_texture.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 0, 255, 128))  # semi-transparent magenta
            ghost_texture.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(ghost_texture, draw_rect)

        # Finally, draw tooltip if hovering
        mouse_pos = pygame.mouse.get_pos()
        self.draw_tooltip(surface, mouse_pos)

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
                    elif self.dragging_icon["type"] == "enemy1":
                        level.add_enemy(mx, my, 1)
                    elif self.dragging_icon["type"] == "enemy2":
                        level.add_enemy(mx, my, 2)
                # End drag
                self.dragging_icon = None 