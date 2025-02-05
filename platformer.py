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
# Custom Confirmation Dialog
# -----------------------
def custom_confirmation_dialog(message, use_title=True, opaque_background=False):
    """
    Display a custom, sleek confirmation dialog.
    
    Parameters:
      - message: The text to display.
      - use_title: If True, a "Confirm" title is shown above the message.
      - opaque_background: If True, a solid black overlay is drawn behind the dialog.
      
    Returns:
      True if the user confirms (clicks OK), False if cancelled (via Cancel or ESC).
    """
    dialog_width = 300
    dialog_height = 150
    dialog_rect = pygame.Rect((SCREEN_WIDTH // 2 - dialog_width // 2,
                               SCREEN_HEIGHT // 2 - dialog_height // 2),
                              (dialog_width, dialog_height))
    dialog_panel = pygame_gui.elements.UIPanel(
        relative_rect=dialog_rect,
        manager=manager,
        object_id="#custom_confirmation_dialog"
    )
    # Optionally display a title.
    if use_title:
        title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, 10), (dialog_width, 30)),
            text="Confirm",
            container=dialog_panel,
            manager=manager,
            object_id="#confirmation_title"
        )
        msg_y = 50
        msg_height = 40
    else:
        msg_y = 10
        msg_height = 60
    message_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((10, msg_y), (dialog_width - 20, msg_height)),
        text=message,
        container=dialog_panel,
        manager=manager,
        object_id="#confirmation_message"
    )
    # OK and Cancel buttons.
    button_width = 100
    button_height = 40
    ok_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((dialog_width // 2 - button_width - 10, dialog_height - button_height - 10),
                                  (button_width, button_height)),
        text="OK",
        container=dialog_panel,
        manager=manager,
        object_id="#confirmation_ok"
    )
    cancel_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((dialog_width // 2 + 10, dialog_height - button_height - 10),
                                  (button_width, button_height)),
        text="Cancel",
        container=dialog_panel,
        manager=manager,
        object_id="#confirmation_cancel"
    )
    
    confirmed = None
    while confirmed is None:
        time_delta = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                confirmed = False
            manager.process_events(event)
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == ok_button:
                    confirmed = True
                elif event.ui_element == cancel_button:
                    confirmed = False
        manager.update(time_delta)
        if opaque_background:
            opaque = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            opaque.fill(BLACK)
            screen.blit(opaque, (0, 0))
        else:
            screen.blit(background, (0, 0))
            screen.blit(overlay, (0, 0))
        manager.draw_ui(screen)
        pygame.display.flip()
    dialog_panel.kill()
    return confirmed

# -----------------------
# Mode Selection UI using pygame_gui
# -----------------------
def mode_selection_loop():
    # Create a panel for mode selection.
    panel_width = 400
    panel_height = 300
    panel_rect = pygame.Rect((SCREEN_WIDTH // 2 - panel_width // 2,
                              SCREEN_HEIGHT // 2 - panel_height // 2),
                             (panel_width, panel_height))
    mode_panel = pygame_gui.elements.UIPanel(
        relative_rect=panel_rect,
        manager=manager,
        object_id="#mode_selection_panel"
    )
    
    title_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((0, 20), (panel_width, 40)),
        text='Select Game Mode',
        container=mode_panel,
        manager=manager
    )
    
    button_width = 200
    button_height = 50
    spacing = 20
    free_play_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(((panel_width - button_width) // 2, 80),
                                  (button_width, button_height)),
        text='Free Play',
        container=mode_panel,
        manager=manager
    )
    level_builder_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(((panel_width - button_width) // 2, 80 + button_height + spacing),
                                  (button_width, button_height)),
        text='Level Builder',
        container=mode_panel,
        manager=manager
    )
    campaign_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(((panel_width - button_width) // 2, 80 + 2 * (button_height + spacing)),
                                  (button_width, button_height)),
        text='Campaign',
        container=mode_panel,
        manager=manager
    )
    
    selected_mode = None
    while selected_mode is None:
        time_delta = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # In the main menu, if ESC is pressed, hide the mode panel and show a confirmation.
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                mode_panel.hide()  # Hide underlying UI
                if custom_confirmation_dialog("Do you want to exit the game?", use_title=True, opaque_background=True):
                    pygame.quit()
                    sys.exit()
                else:
                    mode_panel.show()  # Re-show if cancelled
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
    mode_panel.kill()
    return selected_mode

def show_message(message, duration=2000):
    """Display a message (e.g. 'Coming soon!') for a given duration.
       If ESC is pressed, return immediately."""
    panel = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect((SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 50), (400, 100)),
        manager=manager,
        object_id="#message_panel"
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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                panel.kill()
                return
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
    selected_mode = mode_selection_loop()
    while selected_mode != "Free Play":
        show_message("Coming soon!", duration=2000)
        selected_mode = mode_selection_loop()
    
    # Free Play mode begins.
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
            # In Free Play mode, pressing ESC shows a confirmation to return to the main menu.
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if custom_confirmation_dialog("Return to main menu?", use_title=False, opaque_background=False):
                    selected_mode = mode_selection_loop()
                    while selected_mode != "Free Play":
                        show_message("Coming soon!", duration=2000)
                        selected_mode = mode_selection_loop()
                    # Reset game objects.
                    player = Player(x=100, y=300, width=40, height=40)
                    level = Level()
                    inventory = InventoryPanel(SCREEN_WIDTH, SCREEN_HEIGHT)
                    continue
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
