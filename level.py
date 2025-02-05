import pygame
import math
from slide import SlidePlatform
from enemy import Enemy
from elevator import Elevator, ElevatorPoint
from star import Star
from game_platform import Ground, StonePlatform

BLUE = (0, 0, 255)
LILA = (200, 0, 200)  # new color for trampoline

class Portal:
    def __init__(self, x, y, is_entrance=True, portal_id=1):
        if is_entrance:
            self.image = pygame.image.load('images/portal_entry.png').convert_alpha()
        else:
            self.image = pygame.image.load('images/portal_exit.png').convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (60, 120))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_entrance = is_entrance
        self.portal_id = portal_id
        self.font = pygame.font.SysFont(None, 24)

    def draw(self, surface, is_dragging=False):
        if is_dragging:
            tinted = self.image.copy()
            tinted.fill((255, 0, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(tinted, self.rect)
        else:
            surface.blit(self.image, self.rect)
        text = self.font.render(str(self.portal_id), True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

class Level:
    def __init__(self):
        screen = pygame.display.get_surface()
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Define intended platform dimensions.
        platform_width = 225   # 1.5x original width
        platform_height = 30   # 1.5x original height
        
        # Create platforms using our new classes.
        self.platforms = [
            Ground(0, screen_height - 50, screen_width),  # Ground platform (height defaults to 50)
            StonePlatform(300, 600, platform_width, platform_height),
            StonePlatform(500, 500, platform_width, platform_height),
            StonePlatform(700, 450, platform_width, platform_height),
            StonePlatform(900, 400, platform_width, platform_height),
        ]
        
        self.slides = [
            SlidePlatform(700, 350, 500, 550)
        ]
        self.portals = []
        self.next_portal_id = 1
        
        self.dragging_item = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        # Setup trampoline.
        tramp_texture_orig = pygame.image.load("images/trampoline.png").convert_alpha()
        height_ratio = 40 / tramp_texture_orig.get_height()
        scaled_w = int(tramp_texture_orig.get_width() * height_ratio)
        scaled_h = 40
        self.tramp_texture = pygame.transform.smoothscale(tramp_texture_orig, (scaled_w, scaled_h))
        self.tramp_width = int(40 * (363/198))
        self.trampolines = [
            pygame.Rect(900, 580, self.tramp_width, 40)
        ]
        
        self.enemies = []
        self.elevators = []
        self.next_elevator_id = 1
        self.elevator_prev_positions = {}
        self.stars = []
    
    def handle_mouse_events(self, events):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:  # Right-click: remove item
                    item = self.find_clicked_item(mouse_x, mouse_y)
                    if item:
                        self.remove_item(item)
                elif event.button == 1:  # Left-click: drag or flip slide
                    for slide in self.slides:
                        if slide.handle_click(event.pos):
                            break
                    else:
                        clicked_item = self.find_clicked_item(mouse_x, mouse_y)
                        if clicked_item:
                            self.dragging_item = clicked_item
                            if hasattr(clicked_item, 'rect'):
                                self.drag_offset_x = clicked_item.rect.x - mouse_x
                                self.drag_offset_y = clicked_item.rect.y - mouse_y
                            elif isinstance(clicked_item, SlidePlatform):
                                self.drag_offset_x = clicked_item.start_x - mouse_x
                                self.drag_offset_y = clicked_item.start_y - mouse_y
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_item:
                    mouse_x, mouse_y = event.pos
                    dx = mouse_x + self.drag_offset_x
                    dy = mouse_y + self.drag_offset_y
                    if hasattr(self.dragging_item, 'rect'):
                        self.dragging_item.rect.x = dx
                        self.dragging_item.rect.y = dy
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
        
        if not self.dragging_item:
            hovered_slide = self.find_clicked_item(mouse_x, mouse_y)
            if isinstance(hovered_slide, SlidePlatform):
                if not hasattr(hovered_slide, 'hover_timer'):
                    hovered_slide.hover_timer = 0
                hovered_slide.hover_timer += 1
            for s in self.slides:
                if s is not hovered_slide:
                    if not hasattr(s, 'hover_timer'):
                        s.hover_timer = 0
                    s.hover_timer = 0
    
    def find_clicked_item(self, mouse_x, mouse_y):
        # Check stone platforms (skip the first if desired)
        for p in self.platforms[1:]:
            if p.rect.collidepoint(mouse_x, mouse_y):
                return p
        # Check trampolines
        for t in self.trampolines:
            if t.collidepoint(mouse_x, mouse_y):
                return t
        # Check slides
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
        # Check stars
        for star in self.stars:
            if star.rect.collidepoint(mouse_x, mouse_y) and not star.collected:
                return star
        return None

    def draw(self, surface):
        for platform in self.platforms:
            if platform == self.dragging_item:
                platform.draw_tinted(surface, (255, 0, 255, 128))
            else:
                platform.draw(surface)
        for slide in self.slides:
            if slide == self.dragging_item:
                slide.draw(surface, highlight=True)
            else:
                slide.draw(surface, highlight=False)
        for tramp in self.trampolines:
            if tramp == self.dragging_item:
                texture = self.tramp_texture.copy()
                overlay = pygame.Surface(texture.get_size(), pygame.SRCALPHA)
                overlay.fill((255, 0, 255, 128))
                texture.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                x = tramp.x + (tramp.width - texture.get_width()) // 2
                surface.blit(texture, (x, tramp.y))
            else:
                self.draw_trampoline_with_texture(surface, tramp)
        for portal in self.portals:
            portal.draw(surface, portal == self.dragging_item)
        for enemy in self.enemies:
            if enemy == self.dragging_item:
                enemy.draw(surface, is_dragging=True)
            else:
                enemy.draw(surface)
        for elevator in self.elevators:
            if isinstance(self.dragging_item, ElevatorPoint) and self.dragging_item in [elevator.start_point, elevator.end_point]:
                elevator.draw(surface, self.dragging_item)
            else:
                elevator.draw(surface, None)
        for star in self.stars:
            star.draw(surface, star == self.dragging_item)

    def draw_trampoline_with_texture(self, surface, tramp):
        texture_w = self.tramp_texture.get_width()
        x = tramp.x + (tramp.width - texture_w) // 2
        surface.blit(self.tramp_texture, (x, tramp.y))

    def remove_item(self, item):
        if item in self.platforms:
            self.platforms.remove(item)
        elif item in self.trampolines:
            self.trampolines.remove(item)
        elif item in self.slides:
            self.slides.remove(item)
        elif item in self.portals:
            portal_id = item.portal_id
            self.portals = [p for p in self.portals if p.portal_id != portal_id]
        elif isinstance(item, Enemy):
            self.enemies.remove(item)
        elif isinstance(item, ElevatorPoint):
            for elevator in self.elevators[:]:
                if item in [elevator.start_point, elevator.end_point]:
                    self.elevators.remove(elevator)
                    break
        elif item in self.stars:
            self.stars.remove(item)
        if self.dragging_item == item:
            self.dragging_item = None

    def add_platform(self, x, y):
        new_platform = StonePlatform(x - 112, y - 15, 225, 30)
        self.platforms.append(new_platform)

    def add_slide(self, x, y):
        new_slide = SlidePlatform(start_x=x, start_y=y, end_x=x - 200, end_y=y + 200)
        self.slides.append(new_slide)

    def add_trampoline(self, x, y):
        new_tramp = pygame.Rect(x - self.tramp_width // 2, y - 20, self.tramp_width, 40)
        self.trampolines.append(new_tramp)

    def add_portal(self, x, y):
        entrance = Portal(x - 15, y - 30, is_entrance=True, portal_id=self.next_portal_id)
        exit_portal = Portal(x + 50, y - 30, is_entrance=False, portal_id=self.next_portal_id)
        self.portals.extend([entrance, exit_portal])
        self.next_portal_id += 1

    def find_portal_pair(self, portal):
        for p in self.portals:
            if p.portal_id == portal.portal_id and p.is_entrance != portal.is_entrance:
                return p
        return None

    def add_enemy(self, x, y, enemy_type):
        x = x - 60
        y = y - 60
        self.enemies.append(Enemy(x, y, enemy_type))

    def add_elevator(self, x, y):
        new_elevator = Elevator(x, y, self.next_elevator_id)
        self.elevators.append(new_elevator)
        self.next_elevator_id += 1

    def add_star(self, x, y):
        self.stars.append(Star(x, y))

    def update(self, player):
        elevator_movements = {}
        for elevator in self.elevators:
            other_platforms = self.platforms.copy()
            other_platforms += [e.platform_rect for e in self.elevators if e != elevator]
            prev_pos = elevator.platform_rect.center
            elevator.update(other_platforms)
            current_pos = elevator.platform_rect.center
            elevator_movements[elevator] = (current_pos[0] - prev_pos[0], current_pos[1] - prev_pos[1])
        for enemy in self.enemies:
            is_dragging = enemy == self.dragging_item
            enemy.update(self.platforms, self, elevator_movements, is_dragging)
        for star in self.stars[:]:
            if not star.collected and player.rect.colliderect(star.rect):
                star.collected = True
                player.stars_collected += 1
                player.star_sound.play()
                self.stars.remove(star)
        return elevator_movements

    def check_collisions(self, player_rect):
        for platform in self.platforms:
            if player_rect.colliderect(platform.rect):
                return True
        return False
