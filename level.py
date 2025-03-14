import pygame
import math
from slide import SlidePlatform
from enemy import Enemy
from elevator import Elevator, ElevatorPoint
from star import Star
from game_platform import Ground, StonePlatform
from trampoline import Trampoline
from draggable import Draggable  # For draggable functionality

BLUE = (0, 0, 255)
LILA = (200, 0, 200)  # New color for trampoline

class Portal(Draggable):
    def __init__(self, x, y, is_entrance=True, portal_id=1):
        Draggable.__init__(self)
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

    def draw(self, surface):
        if self.being_dragged:
            tinted = self.get_tinted_surface(self.image)
            surface.blit(tinted, self.rect)
        else:
            surface.blit(self.image, self.rect)
        text = self.font.render(str(self.portal_id), True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

class Level:
    def __init__(self, builder_mode=False):
        screen = pygame.display.get_surface()
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Define intended platform dimensions.
        platform_width = 225   # 1.5x original width
        platform_height = 30   # 1.5x original height
        
        # Create platforms using our new classes.
        self.platforms = [
            Ground(0, screen_height - 50, screen_width),  # Ground platform
            StonePlatform(300, 600, platform_width, platform_height),
            StonePlatform(500, 500, platform_width, platform_height),
            StonePlatform(700, 450, platform_width, platform_height),
            StonePlatform(900, 400, platform_width, platform_height),
        ]
        
        self.slides = [ SlidePlatform(700, 350, 500, 550) ]
        self.portals = []  # List of Portal objects
        self.next_portal_id = 1
        
        self.dragging_item = None
        
        # Create trampolines.
        tramp_width = int(40 * (363/198))
        self.trampolines = [ Trampoline(900, 580, tramp_width, 40) ]
        
        self.enemies = []
        self.elevators = []
        self.next_elevator_id = 1
        self.elevator_prev_positions = {}
        self.stars = []
        self.trashes = []  # New list to hold Trash items
        self.bullets = []  # <--- NEW: List to track active bullets
        
        # ** NEW: Initialize confetti explosions list **
        self.confetti_explosions = []
        
        # Add a few default collectible stars and trash items.
        # Positions are chosen arbitrarily; adjust as desired.
        self.add_star(400, 300)
        self.add_star(800, 250)
        self.add_trash(600, 350)
        self.add_trash(750, 400)
        
        # Initialize tool state for level builder.
        self.current_tool = None
        self.last_spray_time = 0
        self.spray_interval = 100  # milliseconds between placements in spray mode
    
    def handle_mouse_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked_item = self.find_clicked_item(event.pos[0], event.pos[1])
                if clicked_item and hasattr(clicked_item, "handle_click"):
                    action = clicked_item.handle_click(event)
                    if action == "drag":
                        self.dragging_item = clicked_item
                    elif action == "remove":
                        self.remove_item(clicked_item)
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_item and isinstance(self.dragging_item, Draggable):
                    self.dragging_item.update_drag(event.pos[0], event.pos[1])
                keys = pygame.key.get_pressed()
                if self.current_tool is not None and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
                    now = pygame.time.get_ticks()
                    if now - self.last_spray_time > self.spray_interval:
                        self.last_spray_time = now
                        import random
                        offset_x = random.randint(-5, 5)
                        offset_y = random.randint(-5, 5)
                        x, y = event.pos
                        new_x = x + offset_x
                        new_y = y + offset_y
                        tool = self.current_tool
                        if tool == "star":
                            self.add_star(new_x, new_y)
                        elif tool == "platform":
                            self.add_platform(new_x, new_y)
                        elif tool == "slide":
                            self.add_slide(new_x, new_y)
                        elif tool == "trampoline":
                            self.add_trampoline(new_x, new_y)
                        elif tool == "portal":
                            self.add_portal(new_x, new_y)
                        elif tool == "enemy1":
                            self.add_enemy(new_x, new_y, 1)
                        elif tool == "enemy2":
                            self.add_enemy(new_x, new_y, 2)
                        elif tool == "elevator":
                            self.add_elevator(new_x, new_y)
                        elif tool == "trash":
                            self.add_trash(new_x, new_y)
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.dragging_item and isinstance(self.dragging_item, Draggable):
                    self.dragging_item.end_drag()
                self.dragging_item = None
                self.current_tool = None
        
        if not self.dragging_item:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            hovered_slide = self.find_clicked_item(mouse_x, mouse_y)
            if hovered_slide and isinstance(hovered_slide, SlidePlatform):
                if not hasattr(hovered_slide, 'hover_timer'):
                    hovered_slide.hover_timer = 0
                hovered_slide.hover_timer += 1
            for s in self.slides:
                if s is not hovered_slide:
                    if not hasattr(s, 'hover_timer'):
                        s.hover_timer = 0
                    s.hover_timer = 0

    def find_clicked_item(self, mouse_x, mouse_y):
        # Check stone platforms (skip the ground if desired)
        for p in self.platforms[1:]:
            if p.rect.collidepoint(mouse_x, mouse_y):
                return p
        # Check trampolines
        for tramp in self.trampolines:
            if tramp.rect.collidepoint(mouse_x, mouse_y):
                return tramp
        # Check slides (including if the click is on the flip icon)
        for s in self.slides:
            if s.contains_point(mouse_x, mouse_y, threshold=8) or s.flip_icon_contains_point(mouse_x, mouse_y):
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
        # Check trash items
        for trash in self.trashes:
            if trash.rect.collidepoint(mouse_x, mouse_y):
                return trash
        return None

    def draw(self, surface):
        for platform in self.platforms:
            platform.draw(surface)
        for slide in self.slides:
            slide.draw(surface)
        for tramp in self.trampolines:
            tramp.draw(surface)
        for portal in self.portals:
            portal.draw(surface)
        for enemy in self.enemies:
            enemy.draw(surface)
        for elevator in self.elevators:
            elevator.draw(surface)
        for trash in self.trashes:  # New loop to draw trash items
            trash.draw(surface)
        for star in self.stars:
            star.draw(surface)
        # --- NEW: Draw bullets ---
        for bullet in self.bullets:
            bullet.draw(surface)
        # --- NEW: Draw confetti explosions ---
        for explosion in self.confetti_explosions:
            explosion.draw(surface)

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
        elif item in self.trashes:  # New clause for trash
            self.trashes.remove(item)
        if self.dragging_item == item:
            self.dragging_item = None

    def add_platform(self, x, y):
        new_platform = StonePlatform(x - 112, y - 15, 225, 30)
        self.platforms.append(new_platform)

    def add_slide(self, x, y):
        new_slide = SlidePlatform(start_x=x, start_y=y, end_x=x - 200, end_y=y + 200)
        self.slides.append(new_slide)

    def add_trampoline(self, x, y):
        tramp_width = int(40 * (363/198))
        new_tramp = Trampoline(x - tramp_width // 2, y - 20, tramp_width, 40)
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

    def add_trash(self, x, y):
        from trash import Trash  # Import inside the method to avoid circular imports
        new_trash = Trash(x, y)
        self.trashes.append(new_trash)

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
            enemy.update(self.platforms, self, elevator_movements)
        for star in self.stars[:]:
            if not star.collected and player.rect.colliderect(star.rect):
                star.collected = True
                player.stars_collected += 1
                player.star_sound.play()
                self.stars.remove(star)
        
        # --- NEW: Update bullets ---
        screen_obj = pygame.display.get_surface()
        screen_width, screen_height = screen_obj.get_width(), screen_obj.get_height()
        for bullet in self.bullets[:]:
            bullet.update()
            # Remove bullet if off screen
            if bullet.is_off_screen(screen_width, screen_height):
                self.bullets.remove(bullet)
                continue
            # Remove bullet if it hits a platform
            for platform in self.platforms:
                if bullet.rect.colliderect(platform.rect):
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break
            else:
                # Check collision with enemies
                for enemy in self.enemies[:]:
                    if bullet.rect.colliderect(enemy.rect):
                        # Create a massive explosion using 100 particles
                        from confetti import ConfettiExplosion
                        explosion = ConfettiExplosion(enemy.rect.center, num_particles=100)
                        self.confetti_explosions.append(explosion)
                        self.enemies.remove(enemy)
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                        break
                        
        # --- Update confetti explosions ---
        for explosion in self.confetti_explosions[:]:
            explosion.update()
            if explosion.is_finished():
                self.confetti_explosions.remove(explosion)
                
        # --- End bullet update ---
        return elevator_movements

    def check_collisions(self, player_rect):
        for platform in self.platforms:
            if player_rect.colliderect(platform.rect):
                return True
        return False
