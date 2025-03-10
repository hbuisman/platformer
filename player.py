import pygame
from physics_object import PhysicsObject
from slide import SlidePlatform, SlidePhysics

# Constants for the player:
GRAVITY = 0.5
PLAYER_SPEED = 5
JUMP_FORCE = 10

class Player(PhysicsObject):
    def __init__(self, x, y, width, height):
        super().__init__()
        # Increase player size: scale factor increased from 2 to 2.5
        player_scale = 2.5  # Now the player is a tad larger
        self.rect = pygame.Rect(x, y, int(width * player_scale), int(height * player_scale))
        self.jumps_left = 2
        self.on_slide = False

        self.image = pygame.image.load("images/player_big.png").convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (int(width * player_scale), int(height * player_scale)))
        self.image_right = self.image
        self.image_left = pygame.transform.flip(self.image, True, False)
        self.facing_right = True

        self.ouch_sound = pygame.mixer.Sound("sounds/big_player_ouch.wav")
        self.boing_sound = pygame.mixer.Sound("sounds/big_player_boing.wav")
        self.portal_sound = pygame.mixer.Sound("sounds/big_player_portal.wav")

        self.width = int(width * player_scale)
        self.height = int(height * player_scale)
        self.lives = 3
        self.invulnerable_timer = 0
        self.game_over = False

        self.heart_image = pygame.image.load("images/heart.png").convert_alpha()
        self.heart_image = pygame.transform.smoothscale(self.heart_image, (40, 40))

        self.on_elevator = False
        self.stars_collected = 0
        self.star_sound = pygame.mixer.Sound("sounds/collect_star.wav")
        
        # Gun related attributes (always equipped)
        self.gun_image = pygame.image.load("images/gun_lowres.png").convert_alpha()
        gun_scale = 0.20  # Scale down the gun to 20% of its original size
        gun_new_size = (int(self.gun_image.get_width() * gun_scale),
                        int(self.gun_image.get_height() * gun_scale))
        self.gun_image = pygame.transform.smoothscale(self.gun_image, gun_new_size)
        self.gun_image_right = self.gun_image
        self.gun_image_left = pygame.transform.flip(self.gun_image, True, False)
        self.shoot_cooldown = 0

        # NEW: Load the gun shooting sound. Default to "gun.wav"
        self.gun_shoot_sound = pygame.mixer.Sound("sounds/gun.wav")

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
            # Only allow jump if not already moving upward (to avoid multiple jumps per key press)
            if self.y_velocity >= 0:
                self.y_velocity = -JUMP_FORCE
                self.jumps_left -= 1

    def update(self, platforms, slides, trampolines, level, elevator_movements=None):
        # Combine platforms and elevator platforms.
        all_platforms = platforms.copy()
        for elevator in level.elevators:
            all_platforms.append(elevator.platform_rect)
        
        # Update physics (gravity, collisions, portal checks, and trampolines).
        # Because Player overrides check_trampolines, that method will be used.
        self.update_physics(all_platforms, trampolines, level.portals, level)
        
        # If landed, reset jump counter.
        if self.on_ground:
            self.jumps_left = 2

        # Handle elevator movement (as before).
        elevator_collisions = []
        for elevator in level.elevators:
            if self.rect.colliderect(elevator.platform_rect):
                elevator_collisions.append(elevator)
        for elevator in elevator_collisions:
            if self.rect.bottom == elevator.platform_rect.top:
                movement = elevator_movements.get(elevator, (0, 0))
                if not hasattr(self, 'elevator_offset'):
                    self.elevator_offset = (self.rect.x - elevator.platform_rect.x,
                                            self.rect.y - elevator.platform_rect.y)
                self.elevator_offset = (self.elevator_offset[0] + self.x_velocity, self.elevator_offset[1])
                self.rect.x += movement[0]
                self.rect.y += movement[1]
                self.rect.x = elevator.platform_rect.x + self.elevator_offset[0]
                self.rect.y = elevator.platform_rect.y + self.elevator_offset[1]
        if not elevator_collisions and hasattr(self, 'elevator_offset'):
            del self.elevator_offset

        # Handle slide behavior.
        self.check_slides(slides)
        self.ensure_not_below_any_platform(platforms)
        self.check_off_screen()
        if self.invulnerable_timer <= 0:
            self.check_enemy_collisions(level.enemies)
        else:
            self.invulnerable_timer -= 1

        # --- NEW: Gun shooting logic ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_f] and self.shoot_cooldown <= 0:
            from bullet import Bullet  # Import here to avoid circular dependencies
            if self.facing_right:
                bullet_x = self.rect.right
                direction = "right"
            else:
                bullet_x = self.rect.left
                direction = "left"
            bullet_y = self.rect.centery
            level.bullets.append(Bullet(bullet_x, bullet_y, direction))
            # Play the gun shooting sound
            self.gun_shoot_sound.play()
            self.shoot_cooldown = 20  # Cooldown frames between shots
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        # --- End Gun logic ---

    def check_slides(self, slides):
        self.on_slide = False
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
        return abs(self.rect.bottom - physics.alignment_y) < 8

    def align_on_slide(self, slide):
        physics = slide.compute_physics(self.rect.centerx, self.rect.bottom)
        if physics:
            self.rect.bottom = physics.alignment_y
            self.x_velocity = physics.velocity_x
            self.y_velocity = physics.velocity_y

    def ensure_not_below_any_platform(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.rect.bottom > platform.top and self.y_velocity >= 0:
                    self.rect.bottom = platform.top
                    self.y_velocity = 0
                    self.on_slide = False
                    self.on_ground = True

    def check_off_screen(self):
        screen_obj = pygame.display.get_surface()
        if self.rect.top > screen_obj.get_height() or self.rect.right < 0 or self.rect.left > screen_obj.get_width():
            self.lose_life()

    def check_enemy_collisions(self, enemies):
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                self.lose_life()
                break

    def handle_vertical_collisions(self, platforms):
        initial_vy = self.y_velocity
        # Defer collision handling to the parent PhysicsObject implementation.
        super().handle_vertical_collisions(platforms)
        # If a head collision occurred (player bumping upward),
        # just play the ouch sound without losing a life.
        if initial_vy < 0 and self.y_velocity == 0:
            if self.invulnerable_timer <= 0:
                self.ouch_sound.play()

    def lose_life(self):
        if self.invulnerable_timer <= 0:
            self.lives -= 1
            self.invulnerable_timer = 60
            self.ouch_sound.play()
            screen_obj = pygame.display.get_surface()
            self.rect.center = (screen_obj.get_width() // 2, screen_obj.get_height() // 2)
            if self.lives <= 0:
                self.game_over = True

    def check_trampolines(self, trampolines):
        # Override the parent's check_trampolines to play sound and use the correct bounce force.
        for tramp in trampolines:
            if self.rect.colliderect(tramp.rect):
                if self.y_velocity > 0:
                    self.boing_sound.play()
                    self.rect.bottom = tramp.rect.top
                    self.y_velocity = -JUMP_FORCE * 2
                    self.on_ground = False

    def draw(self, surface):
        image_to_draw = self.image_right if self.facing_right else self.image_left
        surface.blit(image_to_draw, self.rect)
        # --- NEW: Draw the gun ---
        gun_image = self.gun_image_right if self.facing_right else self.gun_image_left
        # Position the gun a bit forward. Using half its width with a slight outward offset.
        if self.facing_right:
            gun_offset = (self.rect.right - self.gun_image.get_width() - 2, self.rect.y + self.rect.height // 3)
        else:
            gun_offset = (self.rect.x + 2, self.rect.y + self.rect.height // 3)
        surface.blit(gun_image, gun_offset)

    def draw_hearts(self, surface):
        if self.game_over:
            return
        for i in range(self.lives):
            surface.blit(self.heart_image, (10 + i * 50, 10))

    def change_character(self, new_sprite_path, sound_data):
        """Update the player's appearance and sound effects"""
        # Load and scale new character assets
        original_image = pygame.image.load(new_sprite_path).convert_alpha()
        self.image = pygame.transform.smoothscale(original_image, (self.rect.width, self.rect.height))
        
        # Update directional images
        self.image_right = self.image
        self.image_left = pygame.transform.flip(self.image, True, False)
        
        # Update all sounds
        self.ouch_sound = pygame.mixer.Sound(sound_data["ouch_sound"])
        self.boing_sound = pygame.mixer.Sound(sound_data["boing_sound"])
        self.portal_sound = pygame.mixer.Sound(sound_data["portal_sound"])
        
        # NEW: Update gun shooting sound based on character type
        if "player_small" in new_sprite_path:
            self.gun_shoot_sound = pygame.mixer.Sound("sounds/small_player_shoot.wav")
        else:
            self.gun_shoot_sound = pygame.mixer.Sound("sounds/gun.wav")
        
        # Preserve position with original size
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        
        # Maintain original collision size
        if hasattr(self, 'hitbox'):
            self.hitbox = self.rect.inflate(-20, -10)
