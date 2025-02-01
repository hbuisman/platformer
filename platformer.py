import pygame
import sys
from player import Player  # <-- Import the Player class from player.py
from level import Level   # <-- Import the new Level class
from inventory import InventoryPanel

pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 800
FPS = 60
GRAVITY = 0.5
PLAYER_SPEED = 5
JUMP_FORCE = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)
DIALOG_BG = (40, 40, 40)
BUTTON_COLOR = (60, 60, 60)
BUTTON_HOVER = (80, 80, 80)
BUTTON_TEXT = (255, 255, 255)

# Setup font for UI text
UI_FONT = pygame.font.SysFont(None, 32)  # None uses default system font
INVENTORY_PROMPT = UI_FONT.render("Press I for inventory", True, BLACK)
PROMPT_PADDING = 10  # Padding from screen edge

# Set up fullscreen display
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH = screen.get_width()
SCREEN_HEIGHT = screen.get_height()
pygame.display.set_caption("Basic Platformer")

# Load and scale background image
background = pygame.image.load("images/background.png").convert()
background = pygame.transform.smoothscale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Create a semi-transparent white overlay for fading the background
overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
overlay.fill((255, 255, 255))
overlay.set_alpha(128)  # 128 is half transparent (0 is invisible, 255 is solid)

clock = pygame.time.Clock()

class ExitDialog:
    def __init__(self):
        self.width = 400
        self.height = 200
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        
        # Create buttons
        button_width = 120
        button_height = 40
        button_y = self.y + self.height - 60
        self.yes_button = pygame.Rect(self.x + 60, button_y, button_width, button_height)
        self.no_button = pygame.Rect(self.x + self.width - button_width - 60, button_y, 
                                   button_width, button_height)
        
        # Pre-render text
        self.title_text = UI_FONT.render("Exit Game?", True, WHITE)
        self.yes_text = UI_FONT.render("Yes", True, BUTTON_TEXT)
        self.no_text = UI_FONT.render("No", True, BUTTON_TEXT)
        
        self.yes_hovered = False
        self.no_hovered = False
    
    def handle_mouse(self, pos):
        self.yes_hovered = self.yes_button.collidepoint(pos)
        self.no_hovered = self.no_button.collidepoint(pos)
        return self.yes_hovered or self.no_hovered
    
    def draw(self, surface):
        # Draw semi-transparent background overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        surface.blit(overlay, (0, 0))
        
        # Draw dialog box
        dialog_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, DIALOG_BG, dialog_rect, border_radius=10)
        
        # Draw title
        title_rect = self.title_text.get_rect(centerx=self.x + self.width//2, 
                                             centery=self.y + 50)
        surface.blit(self.title_text, title_rect)
        
        # Draw buttons with hover effect
        yes_color = BUTTON_HOVER if self.yes_hovered else BUTTON_COLOR
        no_color = BUTTON_HOVER if self.no_hovered else BUTTON_COLOR
        
        pygame.draw.rect(surface, yes_color, self.yes_button, border_radius=5)
        pygame.draw.rect(surface, no_color, self.no_button, border_radius=5)
        
        # Draw button text
        yes_text_rect = self.yes_text.get_rect(center=self.yes_button.center)
        no_text_rect = self.no_text.get_rect(center=self.no_button.center)
        surface.blit(self.yes_text, yes_text_rect)
        surface.blit(self.no_text, no_text_rect)

class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y, is_entry=True):
        super().__init__()
        if is_entry:
            self.image = pygame.image.load('images/portal_entry.png').convert_alpha()
        else:
            self.image = pygame.image.load('images/portal_exit.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def main():
    # Create a player and a new Level instance
    player = Player(x=100, y=300, width=40, height=40)  # width/height will be doubled in Player.__init__
    level = Level()
    inventory = InventoryPanel(SCREEN_WIDTH, SCREEN_HEIGHT)
    exit_dialog = None
    
    running = True
    while running:
        clock.tick(FPS)
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if exit_dialog is None:
                    exit_dialog = ExitDialog()
                else:
                    exit_dialog = None
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
                if exit_dialog is None:
                    inventory.toggle(SCREEN_WIDTH)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if exit_dialog is not None:
                    if exit_dialog.yes_button.collidepoint(event.pos):
                        running = False
                    elif exit_dialog.no_button.collidepoint(event.pos):
                        exit_dialog = None
        
        if exit_dialog is None:
            # Normal game updates when dialog is not shown
            level.handle_mouse_events(events)
            for event in events:
                inventory.handle_event(event, level, player)
            player.handle_input()
            player.update(level.platforms, level.slides, level.trampolines, level)
            inventory.update()
        else:
            # Update dialog hover states
            if exit_dialog.handle_mouse(mouse_pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        
        # Draw background with fade effect
        screen.blit(background, (0, 0))
        screen.blit(overlay, (0, 0))  # Apply the semi-transparent overlay

        player.draw(screen)
        # Draw the level
        level.draw(screen)
        # Draw "Press I for inventory" prompt if inventory is closed
        if not inventory.open:
            # Position in top right corner with padding
            prompt_rect = INVENTORY_PROMPT.get_rect()
            prompt_rect.topright = (SCREEN_WIDTH - PROMPT_PADDING, PROMPT_PADDING)
            screen.blit(INVENTORY_PROMPT, prompt_rect)
        # Draw panel last so it sits on top
        inventory.draw(screen)
        
        # Draw exit dialog on top if it exists
        if exit_dialog is not None:
            exit_dialog.draw(screen)

        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 