import sys
import pygame
import pygame_gui
from player import Player         # Import the Player class from player.py
from level import Level           # Import the Level class
from inventory import InventoryPanel

pygame.init()

# -----------------------
# Constants and Settings
# -----------------------
WIDTH, HEIGHT = 1200, 800
FPS = 60
GRAVITY = 0.5
PLAYER_SPEED = 5
JUMP_FORCE = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# -----------------------
# Display Setup
# -----------------------
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH = screen.get_width()
SCREEN_HEIGHT = screen.get_height()
pygame.display.set_caption("Basic Platformer")
clock = pygame.time.Clock()

# -----------------------
# pygame_gui Manager Setup
# -----------------------
manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))

# -----------------------
# Load Background & Overlay
# -----------------------
background = pygame.image.load("images/background.png").convert()
background = pygame.transform.smoothscale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
overlay.fill((255, 255, 255))
overlay.set_alpha(80)  # Semi-transparent overlay

# -----------------------
# Mode Selection UI using pygame_gui
# -----------------------
def mode_selection_loop():
    # Create a panel to contain our buttons.
    panel_width = 400
    panel_height = 300
    panel_rect = pygame.Rect((SCREEN_WIDTH // 2 - panel_width // 2,
                               SCREEN_HEIGHT // 2 - panel_height // 2),
                             (panel_width, panel_height))
    panel = pygame_gui.elements.UIPanel(
        relative_rect=panel_rect,
        manager=manager
    )
    
    # Title Label
    title_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((0, 20), (panel_width, 40)),
        text='Select Game Mode',
        container=panel,
        manager=manager
    )
    
    # Create buttons for each mode.
    button_width = 200
    button_height = 50
    spacing = 20
    free_play_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(((panel_width - button_width) // 2, 80),
                                  (button_width, button_height)),
        text='Free Play',
        container=panel,
        manager=manager
    )
    level_builder_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(((panel_width - button_width) // 2, 80 + button_height + spacing),
                                  (button_width, button_height)),
        text='Level Builder',
        container=panel,
        manager=manager
    )
    campaign_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(((panel_width - button_width) // 2, 80 + 2 * (button_height + spacing)),
                                  (button_width, button_height)),
        text='Campaign',
        container=panel,
        manager=manager
    )
    
    selected_mode = None
    while selected_mode is None:
        time_delta = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            manager.process_events(event)
            
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == free_play_button:
                    selected_mode = "Free Play"
                elif event.ui_element == level_builder_button:
                    selected_mode = "Level Builder"
                elif event.ui_element == campaign_button:
                    selected_mode = "Campaign"
                    
        manager.update(time_delta)
        screen.blit(background, (0, 0))
        screen.blit(overlay, (0, 0))
        manager.draw_ui(screen)
        pygame.display.flip()
    
    panel.kill()
    return selected_mode

def show_message(message, duration=2000):
    """Display a message (e.g. 'Coming soon!') for a given duration using pygame_gui."""
    panel = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect((SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 50), (400, 100)),
        manager=manager
    )
    msg_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((0, 0), (400, 100)),
        text=message,
        container=panel,
        manager=manager
    )
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < duration:
        time_delta = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            manager.process_events(event)
        manager.update(time_delta)
        screen.blit(background, (0, 0))
        screen.blit(overlay, (0, 0))
        manager.draw_ui(screen)
        pygame.display.flip()
    panel.kill()

# -----------------------
# Main Game Loop
# -----------------------
def main():
    # Loop until Free Play is selected.
    selected_mode = mode_selection_loop()
    while selected_mode != "Free Play":
        show_message("Coming soon!", duration=2000)
        selected_mode = mode_selection_loop()
    
    # Continue with Free Play mode.
    player = Player(x=100, y=300, width=40, height=40)
    level = Level()
    inventory = InventoryPanel(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    running = True
    while running:
        time_delta = clock.tick(FPS) / 1000.0
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # (You may insert an exit dialog or inventory toggle here.)
                pass
            inventory.handle_event(event, level, player)
        level.handle_mouse_events(events)
        player.handle_input()
        elevator_movements = level.update(player)
        player.update(level.platforms, level.slides, level.trampolines, level, elevator_movements)
        
        screen.blit(background, (0, 0))
        screen.blit(overlay, (0, 0))
        player.draw(screen)
        player.draw_hearts(screen)
        level.draw(screen)
        inventory.draw(screen)
        pygame.display.flip()
        manager.update(time_delta)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
