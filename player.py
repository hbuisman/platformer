import pygame
from slide import SlidePlatform, SlidePhysics

GRAVITY = 0.5
PLAYER_SPEED = 5
JUMP_FORCE = 10

class Player:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width * 2, height * 2)
        self.x_velocity = 0
        self.y_velocity = 0
        self.jumps_left = 2
        self.on_ground = False
        self.on_slide = False
        self.image = pygame.image.load("images/player_big.png").convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (width * 2, height * 2))
        self.image_right = self.image
        self.image_left = pygame.transform.flip(self.image, True, False)
        self.facing_right = True
        self.ouch_sound = pygame.mixer.Sound("sounds/big_player_ouch.wav")
        self.boing_sound = pygame.mixer.Sound("sounds/big_player_boing.wav")
        self.portal_sound = pygame.mixer.Sound("sounds/big_player_portal.wav")
        self.width = width * 2
        self.height = height * 2
        self.lives = 3
        self.invulnerable_timer = 0
        self.game_over = False
        self.heart_image = pygame.image.load("images/heart.png").convert_alpha()
        self.heart_image = pygame.transform.smoothscale(self.heart_image, (40, 40))
        self.on_elevator = False
        self.stars_collected = 0
        self.star_sound = pygame.mixer.Sound("sounds/collect_star.wav")
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        if not self.on_slide:
            if keys[pygame.K_LEFT]:
                self.x_velocity = -PLAYER_SPEED
                self.facing_right = False
            elif keys[pygame.K_RIGHT]:
                self.x_velocity = PLAYER_SPEED
                self.facing_right = True
            else:
                self.x_velocity = 0
        if keys[pygame.K_SPACE] and self.jumps_left > 0:
            if self.y_velocity >= 0:
                self.y_velocity = -JUMP_FORCE
                self.jumps_left -= 1

    def apply_gravity(self):
        self.y_velocity += GRAVITY

    def update(self, platforms, slides, trampolines, level, elevator_movements=None):
        all_platforms = platforms.copy()
        elevator_collisions = []
        for elevator in level.elevators:
            all_platforms.append(elevator.platform_rect)
            if self.rect.colliderect(elevator.platform_rect):
                elevator_collisions.append(elevator)
        self.y_velocity += GRAVITY
        self.rect.y += self.y_velocity
        self.on_ground = False
        for platform in all_platforms:
            if self.on_elevator and platform not in [e.platform_rect for e in level.elevators]:
                continue
            if self.rect.colliderect(platform):
                if self.y_velocity > 0:
                    self.rect.bottom = platform.top
                    self.y_velocity = 0
                    self.on_ground = True
                    self.jumps_left = 2
                elif self.y_velocity < 0:
                    self.rect.top = platform.bottom
                    self.y_velocity = 0
                    if self.on_elevator:
                        for elevator in elevator_collisions:
                            elevator.reverse_direction()
        for elevator in elevator_collisions:
            if self.rect.bottom == elevator.platform_rect.top:
                movement = elevator_movements.get(elevator, (0, 0))
                if not hasattr(self, 'elevator_offset'):
                    self.elevator_offset = (self.rect.x - elevator.platform_rect.x, self.rect.y - elevator.platform_rect.y)
                self.elevator_offset = (self.elevator_offset[0] + self.x_velocity, self.elevator_offset[1])
                self.rect.x += movement[0]
                self.rect.y += movement[1]
                self.rect.x = elevator.platform_rect.x + self.elevator_offset[0]
                self.rect.y = elevator.platform_rect.y + self.elevator_offset[1]
        self.rect.x += self.x_velocity
        for platform in all_platforms:
            if self.rect.colliderect(platform):
                if self.x_velocity > 0:
                    self.rect.right = platform.left
                elif self.x_velocity < 0:
                    self.rect.left = platform.right
                self.x_velocity = 0
        if not elevator_collisions:
            if hasattr(self, 'elevator_offset'):
                del self.elevator_offset
        self.check_slides(slides)
        self.check_trampolines(trampolines)
        self.check_portals(level.portals, level)
        self.ensure_not_below_any_platform(platforms)
        self.check_off_screen()
        if self.invulnerable_timer <= 0:
            self.check_enemy_collisions(level.enemies)
        else:
            self.invulnerable_timer -= 1
        self.on_elevator = len(elevator_collisions) > 0

    def check_slides(self, slides):
        self.on_slide = False
        self.slide_debug_msg = "Not on slide"
        for slide in slides:
            if self.is_on_slide(slide):
                self.align_on_slide(slide)
                self.on_slide = True
                break

    def is_on_slide(self, slide):
        if not slide.contains_point(self.rect.centerx, self.rect.bottom):
            return False
        physics = slide.compute_physics(self.rect.centerx, self.rect.bottom)
        if not physics:
            return False
        self.slide_debug_msg = f"On slide: y={physics.alignment_y:.2f}, vel=({physics.velocity_x:.1f},{physics.velocity_y:.1f})"
        return abs(self.rect.bottom - physics.alignment_y) < 8

    def align_on_slide(self, slide):
        physics = slide.compute_physics(self.rect.centerx, self.rect.bottom)
        if not physics:
            return
        self.rect.bottom = physics.alignment_y
        self.x_velocity = physics.velocity_x
        self.y_velocity = physics.velocity_y

    def check_trampolines(self, trampolines):
        for tramp in trampolines:
            if self.rect.colliderect(tramp.rect):
                if self.y_velocity > 0:
                    self.boing_sound.play()
                    self.rect.bottom = tramp.rect.top
                    self.y_velocity = -JUMP_FORCE * 2
                    self.on_ground = False

    def check_portals(self, portals, level):
        for portal in portals:
            if portal.is_entrance and self.rect.colliderect(portal.rect):
                exit_portal = level.find_portal_pair(portal)
                if exit_portal:
                    self.portal_sound.play()
                    self.rect.centerx = exit_portal.rect.centerx
                    self.rect.bottom = exit_portal.rect.bottom

    def change_character(self, sprite_path, sound_path):
        self.image = pygame.image.load(sprite_path).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (self.width, self.height))
        self.image_right = self.image
        self.image_left = pygame.transform.flip(self.image, True, False)
        base_sound_path = sound_path.replace("_ouch.wav", "")
        self.ouch_sound = pygame.mixer.Sound(f"{base_sound_path}_ouch.wav")
        self.boing_sound = pygame.mixer.Sound(f"{base_sound_path}_boing.wav")
        self.portal_sound = pygame.mixer.Sound(f"{base_sound_path}_portal.wav")

    def ensure_not_below_any_platform(self, platforms):
        if hasattr(self, 'on_elevator') and self.on_elevator:
            return
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.rect.bottom > platform.top and self.y_velocity >= 0:
                    self.rect.bottom = platform.top
                    self.y_velocity = 0
                    self.on_slide = False
                    self.on_ground = True

    def check_off_screen(self):
        screen = pygame.display.get_surface()
        screen_width, screen_height = screen.get_width(), screen.get_height()
        if self.rect.top > screen_height or self.rect.right < 0 or self.rect.left > screen_width:
            self.lose_life()

    def draw(self, surface):
        image_to_draw = self.image_right if self.facing_right else self.image_left
        surface.blit(image_to_draw, self.rect)

    def draw_hearts(self, surface):
        if self.game_over:
            return
        for i in range(self.lives):
            x = 10 + (i * 50)
            y = 10
            surface.blit(self.heart_image, (x, y))

    def lose_life(self):
        if self.invulnerable_timer <= 0:
            self.lives -= 1
            self.invulnerable_timer = 60
            self.ouch_sound.play()
            screen = pygame.display.get_surface()
            self.rect.center = (screen.get_width() // 2, screen.get_height() // 2)
            if self.lives <= 0:
                self.game_over = True

    def check_enemy_collisions(self, enemies):
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                self.lose_life()
                break
