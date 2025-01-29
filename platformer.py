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

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Basic Platformer")

clock = pygame.time.Clock()

def main():
    # Create a player and a new Level instance
    player = Player(x=100, y=300, width=40, height=40)
    level = Level()
    inventory = InventoryPanel(WIDTH, HEIGHT)
    
    running = True
    while running:
        clock.tick(FPS)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
                # Toggle the panel
                inventory.toggle(WIDTH)
        
        # Let the level handle mouse events for dragging
        level.handle_mouse_events(events)
        # Pass events to the inventory
        for event in events:
            inventory.handle_event(event, level)

        player.handle_input()
        player.update(level.platforms, level.slides, level.trampolines, level)
        
        # Update panel position
        inventory.update()

        screen.fill(WHITE)
        player.draw(screen)
        # Draw the level
        level.draw(screen)
        # Draw panel last so it sits on top
        inventory.draw(screen)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 