import pygame

# Mouse cursors
DEFAULT_CURSOR = pygame.SYSTEM_CURSOR_ARROW
HAND_CURSOR = pygame.SYSTEM_CURSOR_HAND

# SECTION 1: ITEMS FOR LEVEL EDITING (MAIN SCROLLABLE AREA) 
# -------------------------------------------------------------------
# Update icon positions to be in vertical list for scrolling
ICONS = [
    {
        "type": "platform",
        "color": (0, 0, 255),
        "rect": pygame.Rect(0, 40, 150, 30),  # Width reduced from 225 to 150
        "image_path": "images/stone-platform.png"
    },
    {
        "type": "slide",
        "color": (0, 200, 0),
        "rect": pygame.Rect(0, 80, 100, 92),  # y from 50 to 80 (40+30+10)
        "image_path": "images/slide.png"
    },
    {
        "type": "trampoline",
        "color": (200, 0, 200),
        "rect": pygame.Rect(0, 182, 73, 40),  # y from 152 to 182 (80+92+10)
        "image_path": "images/trampoline.png"
    },
    {
        "type": "portal",
        "color": (255, 165, 0),
        "rect": pygame.Rect(0, 232, 60, 120),  # y from 202 to 232 (182+40+10)
        "image_path": "images/portal_entry.png"
    },
    {
        "type": "star",
        "image_path": "images/star.png",
        "rect": pygame.Rect(0, 362, 40, 40)  # y from 332 to 362 (232+120+10)
    },
    {
        "type": "enemy1",
        "color": (255, 0, 0),
        "rect": pygame.Rect(0, 412, 60, 60),  # y from 382 to 412 (362+40+10)
        "image_path": "images/enemy1.png"
    },
    {
        "type": "enemy2", 
        "color": (255, 100, 0),
        "rect": pygame.Rect(0, 482, 60, 60),  # y from 452 to 482 (412+60+10)
        "image_path": "images/enemy2.png"
    },
    {
        "type": "spaghetti_monster",
        "color": (255, 200, 0),  # Choose an appropriate color to represent it
        "rect": pygame.Rect(0, 552, 60, 60),  # Placed 10px below enemy2
        "image_path": "images/spaghetti_monster.png"
    },
    {
        "type": "elevator",
        "color": (100, 100, 255),
        "rect": pygame.Rect(0, 622, 112, 30),  # Shifted down to allow room for spaghetti monster
        "image_path": "images/stone-platform.png"
    },
    {
        "type": "trash",
        "rect": pygame.Rect(0, 662, 40, 40),  # Shifted down accordingly
        "image_path": "images/trash.png"
    }
]

# SECTION 2: CHARACTER SELECTION (FIXED BOTTOM SECTION)
# -------------------------------------------------------------------
# Move these constants ABOVE the CHARACTERS list
PORTRAIT_SIZE = 60  # Moved up before first use
BUTTON_BORDER_COLOR = (100, 100, 100)  # Normal border color
BUTTON_HOVER_COLOR = (255, 255, 255)   # Border color when hovering
BUTTON_BORDER_WIDTH = 2

# Then define CHARACTERS
CHARACTERS = [
    {
        "id": "big",
        "portrait": pygame.image.load("images/player_big_portrait.png"),
        "sprite": "images/player_big.png",
        "ouch_sound": "sounds/big_player_ouch.wav",
        "boing_sound": "sounds/big_player_boing.wav",
        "portal_sound": "sounds/big_player_portal.wav",
        "rect": pygame.Rect(0, 0, PORTRAIT_SIZE, PORTRAIT_SIZE),
        "hovered": False
    },
    {
        "id": "small",
        "portrait": pygame.image.load("images/player_small_portrait.png"),
        "sprite": "images/player_small.png",
        "ouch_sound": "sounds/small_player_ouch.wav",
        "boing_sound": "sounds/small_player_boing.wav",
        "portal_sound": "sounds/small_player_portal.wav",
        "rect": pygame.Rect(0, 0, PORTRAIT_SIZE, PORTRAIT_SIZE),
        "hovered": False
    },
    {
        "id": "boy",
        "portrait": pygame.image.load("images/player_boy_portrait.png"),
        "sprite": "images/player_boy.png",
        "ouch_sound": "sounds/boy_player_ouch.wav",
        "boing_sound": "sounds/boy_player_boing.wav",
        "portal_sound": "sounds/boy_player_portal.wav",
        "rect": pygame.Rect(0, 0, PORTRAIT_SIZE, PORTRAIT_SIZE),
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
    "elevator": {
        "name": "Elevator Platform",
        "description": "A moving platform that travels between two points.",
    },
    "spaghetti_monster": {
        "name": "Spaghetti Monster",
        "description": "A monstrous mess of noodles and sauce.",
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

        # Add star to textures (in the existing loop)
        for icon in ICONS:
            if "image_path" in icon:
                if icon["type"] == "star":
                    original = pygame.image.load(icon["image_path"]).convert_alpha()
                    scaled = pygame.transform.smoothscale(
                        original,
                        (icon["rect"].width, icon["rect"].height)
                    )
                    self.textures[icon["type"]] = scaled

        # Add scrolling properties
        self.scroll_offset = 0  # How much we've scrolled down
        self.max_scroll = 0
        self.scroll_speed = 20
        
        # Calculate total content height for scrolling
        self.content_height = max(icon["rect"].bottom for icon in ICONS)
        
        # Character section setup
        self.char_section_height = 100  # Space at bottom for characters
        self.char_section_y = screen_height - self.char_section_height
        
        # Update max scroll based on available space
        available_height = screen_height - self.char_section_height
        self.max_scroll = max(0, self.content_height - available_height)
        
        # Setup character selection horizontal scrolling parameters
        self.char_total_width = len(CHARACTERS) * PORTRAIT_SIZE + (len(CHARACTERS) - 1) * 10
        if self.char_total_width <= self.width:
            self.char_base_x = (self.width - self.char_total_width) // 2
        else:
            self.char_base_x = 0
        self.char_scroll_offset = 0
        self.char_max_scroll = max(0, self.char_total_width - self.width)

    def toggle(self, screen_width):
        self.open = not self.open
        if self.open:
            self.goal_x = screen_width - self.width
            print(f"Opening panel: goal_x = {self.goal_x}")  # Debug print
        else:
            self.goal_x = screen_width
            print(f"Closing panel: goal_x = {self.goal_x}")  # Debug print

    def update_icon_hover_states(self, mouse_pos):
        """Updated to account for scrolling"""
        if not self.dragging_icon:
            self.hovered_icon = None
            panel_rect = pygame.Rect(self.x, 0, self.width, self.height)
            if panel_rect.collidepoint(*mouse_pos):
                # Adjust mouse Y for scrolling
                my_adj = mouse_pos[1] + self.scroll_offset
                for icon in ICONS:
                    abs_rect = icon["rect"].copy()
                    abs_rect.x += self.x
                    abs_rect.y += self.scroll_offset  # Apply scroll offset
                    if abs_rect.collidepoint(mouse_pos[0], my_adj):
                        self.hovered_icon = icon
                        break

    def update_character_hover_states(self, mouse_pos):
        """Updated to only check bottom section with horizontal scrolling."""
        mx, my = mouse_pos
        is_hovering_any = False
        for i, char in enumerate(CHARACTERS):
            rect_copy = char["rect"].copy()
            # Recalculate x using the base value, index spacing, and current scroll offset
            rect_copy.x = self.char_base_x + i * (PORTRAIT_SIZE + 10) + self.char_scroll_offset + self.x
            rect_copy.y = 20 + self.char_section_y  # fixed vertical position within character section
            char["hovered"] = self.open and rect_copy.collidepoint(mx, my)
            if char["hovered"]:
                is_hovering_any = True
        pygame.mouse.set_cursor(HAND_CURSOR if is_hovering_any else DEFAULT_CURSOR)

    def update(self):
        # Animate panel sliding in/out more quickly
        step = 40  # Increase step size for faster animation
        if abs(self.x - self.goal_x) < step:
            self.x = self.goal_x  # Snap to final position if very close
        elif self.x < self.goal_x:
            self.x += step
        elif self.x > self.goal_x:
            self.x -= step
        
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
        
        # Draw "Level Elements" title (scrolls with content)
        font = pygame.font.SysFont(None, 28)
        title_surf = font.render("Level Elements", True, (255, 255, 255))
        title_rect = title_surf.get_rect(x=self.x + 10, y=10 + self.scroll_offset)
        surface.blit(title_surf, title_rect)

        # Draw inventory icons with scroll offset
        for icon in ICONS:
            rect_copy = icon["rect"].copy()
            rect_copy.x += self.x
            rect_copy.y += self.scroll_offset  # Apply scrolling
            
            # Only draw if visible in viewport
            if rect_copy.bottom > 0 and rect_copy.top < self.char_section_y:
                if icon == self.hovered_icon and not self.dragging_icon:
                    # Use the same magenta hue as with drag for consistent UX
                    hover_texture = self.textures[icon["type"]].copy()
                    overlay = pygame.Surface(hover_texture.get_size(), pygame.SRCALPHA)
                    overlay.fill((255, 0, 255, 128))  # semi-transparent magenta
                    hover_texture.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    surface.blit(hover_texture, rect_copy)
                
                surface.blit(self.textures[icon["type"]], rect_copy)
            
            # Remove border – no more pygame.draw.rect(...) around icons

        # Draw "Characters" title above the section
        char_title_surf = font.render("Characters", True, (255, 255, 255))
        char_title_rect = char_title_surf.get_rect(
            centerx=self.x + self.width//2,
            y=self.char_section_y - 30
        )
        surface.blit(char_title_surf, char_title_rect)

        # Draw character section background
        char_bg = pygame.Surface((self.width, self.char_section_height), pygame.SRCALPHA)
        char_bg.fill((140, 140, 140, 200))  # Slightly darker background
        surface.blit(char_bg, (self.x, self.char_section_y))
        
        # Draw character portraits
        for i, char in enumerate(CHARACTERS):
            rect_copy = char["rect"].copy()
            rect_copy.x = self.char_base_x + i * (PORTRAIT_SIZE + 10) + self.char_scroll_offset + self.x
            rect_copy.y = 20 + self.char_section_y  # offset to bottom section
            border_color = BUTTON_HOVER_COLOR if char["hovered"] else BUTTON_BORDER_COLOR
            pygame.draw.rect(surface, border_color, rect_copy, BUTTON_BORDER_WIDTH)
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
        
        if event.type == pygame.MOUSEWHEEL:
            if self.open:
                mx, my = pygame.mouse.get_pos()
                if my >= self.char_section_y:
                    # Scroll horizontally for character selection
                    self.char_scroll_offset -= event.y * self.scroll_speed
                    self.char_scroll_offset = max(-self.char_max_scroll, min(self.char_scroll_offset, 0))
                else:
                    # Vertical scroll for icons
                    self.scroll_offset += event.y * self.scroll_speed
                    self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
        
        # Process character clicks (if applicable)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, char in enumerate(CHARACTERS):
                rect_copy = char["rect"].copy()
                rect_copy.x = self.char_base_x + i * (PORTRAIT_SIZE + 10) + self.char_scroll_offset + self.x
                rect_copy.y = 20 + self.char_section_y
                if rect_copy.collidepoint(event.pos):
                    sound_data = {
                        "ouch_sound": char["ouch_sound"],
                        "boing_sound": char["boing_sound"],
                        "portal_sound": char["portal_sound"]
                    }
                    player.change_character(char["sprite"], sound_data)
                    return
            
            # Check if clicked on any icon in the panel.
            mx, my = event.pos
            for icon in ICONS:
                abs_rect = icon["rect"].copy()
                abs_rect.x += self.x
                if abs_rect.collidepoint(mx, my):
                    # For any icon, assign its type as the active tool.
                    level.current_tool = icon["type"]
                    self.dragging_icon = icon  # for drag-drop behavior
                    break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging_icon:
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
                    elif self.dragging_icon["type"] == "spaghetti_monster":
                        level.add_enemy(mx, my, "spaghetti_monster")
                    elif self.dragging_icon["type"] == "elevator":
                        level.add_elevator(mx, my)
                    elif self.dragging_icon["type"] == "star":
                        level.add_star(mx, my)
                    elif self.dragging_icon["type"] == "trash":
                        level.add_trash(mx, my)
                self.dragging_icon = None 