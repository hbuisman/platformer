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
# Load Star Icon (for star counter)
# -----------------------
star_icon = pygame.image.load("images/star.png").convert_alpha()
star_icon = pygame.transform.smoothscale(star_icon, (40, 40))

# Load Trash Icon (for trash counter)
trash_icon = pygame.image.load("images/trash.png").convert_alpha()
trash_icon = pygame.transform.smoothscale(trash_icon, (35, 35))

# Load Trash Sound (plays when trash is collected)
trash_sound = pygame.mixer.Sound("sounds/crumple.wav")

# -----------------------
# Custom Confirmation Dialog
# -----------------------
def custom_confirmation_dialog(message, use_title=True, opaque_background=False):
    """
    Display a custom, sleek confirmation dialog.
    
    Parameters:
      - message: The text to display.
      - use_title: If True, a "Confirm" title is shown; if False, only the message is displayed.
      - opaque_background: If True, a solid black overlay is drawn behind the dialog.
      
    Returns:
      True if the user clicks OK, False otherwise.
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
# Helper function: Same as draggable.py's get_tinted_surface but at module level.
def get_tinted_surface(surface, tint_color=(255, 255, 255, 80)):
    """
    Return a tinted copy of the given surface, highlighting only its non-transparent parts.
    """
    tinted = surface.copy()
    overlay = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
    overlay.fill(tint_color)
    tinted.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted

# -----------------------
# Mode Selection UI using pygame_gui
# -----------------------
def mode_selection_loop():
    # Load and scale the menu background image.
    menu_image = pygame.image.load("images/menu.png").convert_alpha()
    # Use the original menu image height (1536) to compute the scale factor for screen height.
    scale_factor = SCREEN_HEIGHT / 1536  
    menu_width = int(3072 * scale_factor)
    menu_scaled = pygame.transform.smoothscale(menu_image, (menu_width, SCREEN_HEIGHT))

    # Calculate horizontal crop offset if the scaled width is larger than the screen width.
    crop_offset = (menu_width - SCREEN_WIDTH) // 2 if menu_width > SCREEN_WIDTH else 0

    # Load and scale button images.
    free_play_img = pygame.image.load("images/free_play_button.png").convert_alpha()
    free_play_img = pygame.transform.smoothscale(free_play_img, (int(507 * scale_factor), int(246 * scale_factor)))
    
    level_builder_img = pygame.image.load("images/level_builder_button.png").convert_alpha()
    level_builder_img = pygame.transform.smoothscale(level_builder_img, (int(522 * scale_factor), int(252 * scale_factor)))
    
    campaign_img = pygame.image.load("images/campaign_button.png").convert_alpha()
    campaign_img = pygame.transform.smoothscale(campaign_img, (int(561 * scale_factor), int(267 * scale_factor)))

    # Calculate button positions using scaled coordinates.
    free_play_rect = free_play_img.get_rect()
    free_play_rect.x = int(1270 * scale_factor) - crop_offset
    free_play_rect.y = int(280 * scale_factor)

    level_builder_rect = level_builder_img.get_rect()
    level_builder_rect.x = int(1263 * scale_factor) - crop_offset
    level_builder_rect.y = int(504 * scale_factor)

    campaign_rect = campaign_img.get_rect()
    campaign_rect.x = int(1245 * scale_factor) - crop_offset
    campaign_rect.y = int(745 * scale_factor)

    # Precompute tinted versions of the button images.
    free_play_tinted = get_tinted_surface(free_play_img, (255, 255, 255, 80))
    level_builder_tinted = get_tinted_surface(level_builder_img, (255, 255, 255, 80))
    campaign_tinted = get_tinted_surface(campaign_img, (255, 255, 255, 80))

    selected_mode = None
    while selected_mode is None:
        time_delta = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if custom_confirmation_dialog("Do you want to exit the game?", use_title=True, opaque_background=True):
                        pygame.quit()
                        sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if free_play_rect.collidepoint(mouse_pos):
                    selected_mode = "Free Play"
                elif level_builder_rect.collidepoint(mouse_pos):
                    selected_mode = "Level Builder"
                elif campaign_rect.collidepoint(mouse_pos):
                    selected_mode = "Campaign"

        # Update mouse cursor and highlight buttons on hover.
        mouse_pos = pygame.mouse.get_pos()
        if free_play_rect.collidepoint(mouse_pos) or level_builder_rect.collidepoint(mouse_pos) or campaign_rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # Draw the menu background (cropped to center horizontally) and the button images.
        screen.fill(BLACK)
        screen.blit(menu_scaled, (-crop_offset, 0))

        # Draw free play button; if hovered, use precomputed tinted version
        if free_play_rect.collidepoint(mouse_pos):
            screen.blit(free_play_tinted, free_play_rect)
        else:
            screen.blit(free_play_img, free_play_rect)

        # Draw level builder button; if hovered, use precomputed tinted version
        if level_builder_rect.collidepoint(mouse_pos):
            screen.blit(level_builder_tinted, level_builder_rect)
        else:
            screen.blit(level_builder_img, level_builder_rect)

        # Draw campaign button; if hovered, use precomputed tinted version
        if campaign_rect.collidepoint(mouse_pos):
            screen.blit(campaign_tinted, campaign_rect)
        else:
            screen.blit(campaign_img, campaign_rect)

        pygame.display.flip()
    return selected_mode

def show_message(message, duration=2000):
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

def display_overlay_message(message, duration=3000):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)  # Adjust transparency as needed
    overlay.fill((50, 50, 50))  # Slightly transparent grey
    screen.blit(overlay, (0, 0))
    text = pygame.font.SysFont(None, 64).render(message, True, (245, 245, 245))  # Soft white text
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < duration:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
        pygame.time.delay(10)

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
    player.trash_collected = 0  # Initialize trash counter
    level = Level()
    inventory = InventoryPanel(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    running = True
    while running:
        time_delta = clock.tick(FPS) / 1000.0
        events = pygame.event.get()
        
        # Handle events first
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if custom_confirmation_dialog("Return to main menu?", use_title=False, opaque_background=False):
                    selected_mode = mode_selection_loop()
                    while selected_mode != "Free Play":
                        show_message("Coming soon!", duration=2000)
                        selected_mode = mode_selection_loop()
                    player = Player(x=100, y=300, width=40, height=40)
                    player.trash_collected = 0  # Reset trash counter
                    level = Level()
                    inventory = InventoryPanel(SCREEN_WIDTH, SCREEN_HEIGHT)
                    continue
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
                inventory.toggle(SCREEN_WIDTH)
            inventory.handle_event(event, level, player)
            
            # Wenn auf den Spieler geklickt wird, alle gegnerischen Steuerungen zurücksetzen.
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if player.rect.collidepoint(event.pos):
                    for enemy in level.enemies:
                        enemy.controlled = False
        
        # Add this line to update inventory panel position
        inventory.update()
        
        level.handle_mouse_events(events)
        # Alte Zeile:
        # player.handle_input()

        # Neue Logik: Falls ein Monster gesteuert wird, dieses bewegen,
        # sonst den Spieler steuern.
        controlled_enemy = None
        for enemy in level.enemies:
            if getattr(enemy, "controlled", False):
                controlled_enemy = enemy
                break

        if controlled_enemy:
            controlled_enemy.handle_input()
        else:
            player.handle_input()
        
        elevator_movements = level.update(player)
        
        # Check for trash collection
        for trash in level.trashes[:]:
            if player.rect.colliderect(trash.rect):
                level.trashes.remove(trash)
                player.trash_collected += 1
                trash_sound.play()
        
        player.update(level.platforms, level.slides, level.trampolines, level, elevator_movements)
        
        screen.blit(background, (0, 0))
        screen.blit(overlay, (0, 0))
        player.draw(screen)
        player.draw_hearts(screen)
        level.draw(screen)
        inventory.draw(screen)
        # Draw combined counters for stars and trash in the top right
        margin = 20
        gap_inside = 10
        block_gap = 20

        star_text = pygame.font.SysFont(None, 32).render(f"× {player.stars_collected}", True, BLACK)
        trash_text = pygame.font.SysFont(None, 32).render(f"× {player.trash_collected}", True, BLACK)

        star_block_width = 40 + gap_inside + star_text.get_width()
        trash_block_width = 35 + gap_inside + trash_text.get_width()  # trash icon is 35 wide
        total_counters_width = star_block_width + block_gap + trash_block_width

        # Instead of SCREEN_WIDTH, use inventory.x so that the counters slide with the inventory panel.
        start_x = inventory.x - total_counters_width - margin
        y = 20

        # Draw star counter block (icon and text)
        screen.blit(star_icon, (start_x, y))
        screen.blit(star_text, (start_x + 40 + gap_inside, y + 10))

        # Draw trash counter block (icon and text)
        trash_block_x = start_x + star_block_width + block_gap
        screen.blit(trash_icon, (trash_block_x, y + (40 - 35) // 2))  # center vertically since trash icon is smaller
        screen.blit(trash_text, (trash_block_x + 35 + gap_inside, y + 10))
        
        pygame.display.flip()
        
        # Check for Game Over: if player's lives are finished, display message and reset game.
        if player.lives <= 0:
            display_overlay_message("Game Over", duration=3000)
            selected_mode = mode_selection_loop()
            player = Player(x=100, y=300, width=40, height=40)
            player.trash_collected = 0  # Reset trash counter
            level = Level()
            inventory = InventoryPanel(SCREEN_WIDTH, SCREEN_HEIGHT)
            continue
        
        # Check for Level Win: if all trash has been collected, display win message and reset game.
        if len(level.trashes) == 0:
            display_overlay_message("You Win!", duration=3000)
            selected_mode = mode_selection_loop()
            player = Player(x=100, y=300, width=40, height=40)
            player.trash_collected = 0
            level = Level()
            inventory = InventoryPanel(SCREEN_WIDTH, SCREEN_HEIGHT)
            continue
        
        manager.update(time_delta)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
