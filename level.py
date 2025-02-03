import pygame
import math
from slide import SlidePlatform  # Add this at the top with other imports
from enemy import Enemy
from elevator import Elevator, ElevatorPoint

BLUE = (0, 0, 255)
LILA = (200, 0, 200)  # new color for trampoline

class Portal:
    def __init__(self, x, y, is_entrance=True, portal_id=1):
        # Create the sprite
        if is_entrance:
            self.image = pygame.image.load('images/portal_entry.png').convert_alpha()
        else:
            self.image = pygame.image.load('images/portal_exit.png').convert_alpha()
        
        # Scale the portal image to twice the original size (60x120 instead of 30x60)
        self.image = pygame.transform.smoothscale(self.image, (60, 120))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.is_entrance = is_entrance
        self.portal_id = portal_id
        self.font = pygame.font.SysFont(None, 24)
    
    def draw(self, surface, is_dragging=False):
        if is_dragging:
            # Create a copy of the image with magenta tint for dragging
            tinted = self.image.copy()
            tinted.fill((255, 0, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(tinted, self.rect)
        else:
            # Draw the normal portal sprite
            surface.blit(self.image, self.rect)
        
        # Draw portal number
        text = self.font.render(str(self.portal_id), True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

class Level:
    def __init__(self):
        # Get screen dimensions for proper platform placement
        screen = pygame.display.get_surface()
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Make platforms 1.5x larger (original width was 150, height was 20)
        platform_width = 225  # 150 * 1.5
        platform_height = 30  # 20 * 1.5
        
        # You can define platforms here or load them from a file, etc.
        self.platforms = [
            pygame.Rect(0, screen_height - 50, screen_width, 50),  # Floor at bottom of screen
            pygame.Rect(300, 600, platform_width, platform_height),  # Lower platform
            pygame.Rect(500, 500, platform_width, platform_height),  # Middle platform
            pygame.Rect(700, 450, platform_width, platform_height),  # Another one for vertical stepping
            pygame.Rect(900, 400, platform_width, platform_height),  # A bit higher
        ]
        
        self.slides = [
            SlidePlatform(700, 350, 500, 550)
        ]
        self.portals = []  # Will store Portal objects
        self.next_portal_id = 1

        # Add dragging state
        self.dragging_item = None
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
        height_ratio = platform_height / stone_texture_orig.get_height()
        scaled_w = int(stone_texture_orig.get_width() * height_ratio)
        scaled_h = platform_height
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

        self.enemies = []  # Add list to store enemies
        self.elevators = []  # List to store elevators
        self.next_elevator_id = 1

        self.elevator_prev_positions = {} # Store previous positions of elevators

    def handle_mouse_events(self, events):
        # Always get current mouse position at the start
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:  # right-click -> remove item
                    item = self.find_clicked_item(mouse_x, mouse_y)
                    if item:
                        self.remove_item(item)
                elif event.button == 1:  # left-click
                    # First check for slide flipping
                    for slide in self.slides:
                        if slide.handle_click(event.pos):
                            break  # Stop checking once a click is handled
                    # If no slide was flipped, handle dragging
                    else:
                        clicked_item = self.find_clicked_item(mouse_x, mouse_y)
                        if clicked_item:
                            self.dragging_item = clicked_item
                            # Store offset from mouse to item origin
                            if isinstance(clicked_item, (Portal, Enemy, ElevatorPoint)):
                                self.drag_offset_x = clicked_item.rect.x - mouse_x
                                self.drag_offset_y = clicked_item.rect.y - mouse_y
                            elif isinstance(clicked_item, pygame.Rect):
                                self.drag_offset_x = clicked_item.x - mouse_x
                                self.drag_offset_y = clicked_item.y - mouse_y
                            elif isinstance(clicked_item, SlidePlatform):
                                self.drag_offset_x = clicked_item.start_x - mouse_x
                                self.drag_offset_y = clicked_item.start_y - mouse_y

            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_item:
                    mouse_x, mouse_y = event.pos
                    dx = mouse_x + self.drag_offset_x
                    dy = mouse_y + self.drag_offset_y

                    if isinstance(self.dragging_item, (Portal, Enemy, ElevatorPoint)):
                        self.dragging_item.rect.x = dx
                        self.dragging_item.rect.y = dy
                    elif isinstance(self.dragging_item, pygame.Rect):
                        self.dragging_item.x = dx
                        self.dragging_item.y = dy
                    elif isinstance(self.dragging_item, SlidePlatform):
                        slide = self.dragging_item
                        delta_x = dx - slide.start_x
                        delta_y = dy - slide.start_y
                        slide.start_x += delta_x
                        slide.start_y += delta_y
                        slide.end_x += delta_x
                        slide.end_y += delta_y
                        slide.rect = slide._calculate_rect()
                        slide._update_flip_icon_position()

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging_item = None

        # After processing events, handle hovering
        if not self.dragging_item:
            hovered_slide = self.find_clicked_item(mouse_x, mouse_y)
            if isinstance(hovered_slide, SlidePlatform):
                # Safely access/create hover_timer
                if not hasattr(hovered_slide, 'hover_timer'):
                    hovered_slide.hover_timer = 0
                hovered_slide.hover_timer += 1
            for s in self.slides:
                if s is not hovered_slide:
                    if not hasattr(s, 'hover_timer'):
                        s.hover_timer = 0
                    s.hover_timer = 0

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
        # Check slides (use new contains_point method)
        for s in self.slides:
            if s.contains_point(mouse_x, mouse_y, threshold=8):
                return s
        # Check portals
        for portal in self.portals:
            if portal.rect.collidepoint(mouse_x, mouse_y):
                return portal
        # Check enemies
        for enemy in self.enemies:
            if enemy.rect.collidepoint(mouse_x, mouse_y):
                return enemy
        # Check elevator points
        for elevator in self.elevators:
            if elevator.start_point.rect.collidepoint(mouse_x, mouse_y):
                return elevator.start_point
            if elevator.end_point.rect.collidepoint(mouse_x, mouse_y):
                return elevator.end_point
        return None

    def draw(self, surface):
        # Draw ground (first platform)
        ground = self.platforms[0]
        self.draw_ground_with_texture(surface, ground)

        # Draw other platforms
        for platform in self.platforms[1:]:
            if platform == self.dragging_item:
                # Draw platform with magenta tint when dragging
                texture = self.stone_texture.copy()
                overlay = pygame.Surface(texture.get_size(), pygame.SRCALPHA)
                overlay.fill((255, 0, 255, 128))
                texture.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                # Tile the tinted texture
                for x in range(platform.x, platform.x + platform.width, texture.get_width()):
                    surface.blit(texture, (x, platform.y))
            else:
                # Draw stone texture normally
                self.draw_platform_with_texture(surface, platform)

        # Draw slides
        for slide in self.slides:
            if slide == self.dragging_item:
                # Let the slide draw itself with magenta tint
                slide.draw(surface, highlight=True)
            else:
                slide.draw(surface, highlight=False)

        # Draw trampolines
        for tramp in self.trampolines:
            if tramp == self.dragging_item:
                # Draw trampoline with magenta tint when dragging
                texture = self.tramp_texture.copy()
                overlay = pygame.Surface(texture.get_size(), pygame.SRCALPHA)
                overlay.fill((255, 0, 255, 128))
                texture.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                x = tramp.x + (tramp.width - texture.get_width()) // 2
                surface.blit(texture, (x, tramp.y))
            else:
                self.draw_trampoline_with_texture(surface, tramp)

        # Draw portals
        for portal in self.portals:
            portal.draw(surface, portal == self.dragging_item)

        # Draw enemies
        for enemy in self.enemies:
            if enemy == self.dragging_item:
                enemy.draw(surface, is_dragging=True)
            else:
                enemy.draw(surface)

        # Draw elevators
        for elevator in self.elevators:
            if isinstance(self.dragging_item, ElevatorPoint) and \
               self.dragging_item in [elevator.start_point, elevator.end_point]:
                elevator.draw(surface, self.dragging_item)
            else:
                elevator.draw(surface, None)

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
        elif isinstance(item, Enemy):
            self.enemies.remove(item)
        elif isinstance(item, ElevatorPoint):
            # Find and remove the elevator that this point belongs to
            for elevator in self.elevators[:]:  # Create copy to avoid modification during iteration
                if item in [elevator.start_point, elevator.end_point]:
                    self.elevators.remove(elevator)
                    break
        if self.dragging_item == item:
            self.dragging_item = None

    def add_platform(self, x, y):
        # Create a new platform at the mouse position, 1.5x larger
        new_rect = pygame.Rect(x - 112, y - 15, 225, 30)  # Centered on mouse
        self.platforms.append(new_rect)

    def add_slide(self, x, y):
        # Create a new Slide at (x, y) that slopes down-left like the initial slide
        new_slide = SlidePlatform(
            start_x=x,
            start_y=y,
            end_x=x - 200,  # Move 200px left like the initial slide
            end_y=y + 200   # Move 200px down like the initial slide
        )
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

    def add_enemy(self, x, y, enemy_type):
        """Add a new enemy at the specified position"""
        # Center enemy on mouse position, accounting for 120x120 size
        x = x - 60  # Half of enemy width
        y = y - 60  # Half of enemy height
        self.enemies.append(Enemy(x, y, enemy_type))

    def add_elevator(self, x, y):
        """Add a new elevator at the specified position"""
        new_elevator = Elevator(x, y, self.next_elevator_id)
        self.elevators.append(new_elevator)
        self.next_elevator_id += 1

    def update(self):
        """Update all dynamic elements in the level"""
        elevator_movements = {}
        for elevator in self.elevators:
            # Get all platforms except this elevator's own
            other_platforms = self.platforms.copy()
            other_platforms += [e.platform_rect for e in self.elevators if e != elevator]
            
            prev_pos = elevator.platform_rect.center
            elevator.update(other_platforms)  # Pass collision platforms
            current_pos = elevator.platform_rect.center
            elevator_movements[elevator] = (current_pos[0] - prev_pos[0], 
                                         current_pos[1] - prev_pos[1])
        return elevator_movements

    def add_slide(self, x, y):
        # Create a new Slide at (x, y) that slopes down-left like the initial slide
        new_slide = SlidePlatform(
            start_x=x,
            start_y=y,
            end_x=x - 200,  # Move 200px left like the initial slide
            end_y=y + 200   # Move 200px down like the initial slide
        )
        self.slides.append(new_slide)

    def check_collisions(self, player_rect):
        """Check collisions between player and all level elements"""
        # Check platforms
        for platform in self.platforms + [e.platform_rect for e in self.elevators]:
            if player_rect.colliderect(platform):
                return True
        # Check other elements...
        return False 