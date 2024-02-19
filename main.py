import pygame
from pygame.locals import *
from particle import Sand, Water, Stone, particles, grid, gridSize  # Import from your particles.py

# Initialize Pygame and set up the window
pygame.init()
window_size = (800, 600)
screen = pygame.display.set_mode(window_size, RESIZABLE)
pygame.display.set_caption("Particle Simulation")
clock = pygame.time.Clock()
pygame.font.init()  # Initialize the font module
info_font = pygame.font.SysFont("arial", 18)  # Create a font object


# Global variables
brushSize = 6
paused = False  # Index to select particle type, corresponds to particleTypes list
frameRates = []

# Particle types available for use
particleTypes = [Sand, Water, Stone]


# Utility functions
def screen_to_grid(x, y):
    grid_x = int(x / window_size[0] * gridSize)
    grid_y = int(y / window_size[1] * gridSize)
    return grid_x, grid_y


def add_particles(mouse_x, mouse_y, button, selectedType):

    if button == 1:  # Left mouse button for adding particles
        for dy in range(-brushSize, brushSize + 1):
            for dx in range(-brushSize, brushSize + 1):
                if dx**2 + dy**2 <= brushSize**2:  # Circular brush shape
                    grid_x, grid_y = screen_to_grid(mouse_x + dx * (window_size[0] // gridSize),
                                                    mouse_y + dy * (window_size[1] // gridSize))
                    if 0 <= grid_x < gridSize and 0 <= grid_y < gridSize:
                        offset = grid_y * gridSize + grid_x
                        if not grid[offset]:  # Check if the grid position is empty
                            particle_class = particleTypes[selectedType]
                            new_particle = particle_class({'offset': offset, 'position': {'x': grid_x, 'y': grid_y}})
                            particles.append(new_particle)
                            grid[offset] = new_particle

    elif button == 3:  # Right mouse button for removing particles
        grid_x, grid_y = screen_to_grid(mouse_x, mouse_y)
        for dy in range(-brushSize, brushSize + 1):
            for dx in range(-brushSize, brushSize + 1):
                if dx**2 + dy**2 <= brushSize**2:  # Circular brush shape
                    x, y = grid_x + dx, grid_y + dy
                    if 0 <= x < gridSize and 0 <= y < gridSize:
                        offset = y * gridSize + x
                        if grid[offset]:  # Check if there's a particle to remove
                            particles.remove(grid[offset])
                            grid[offset] = None


def update_simulation():
    # Update particle positions
    for particle in particles:
        particle.update(window_size, screen)

    # Clear screen and redraw all particles
    screen.fill((0, 0, 0))
    for particle in particles:
        particle.display(window_size, screen)


def display_info():
    # Calculate FPS
    fps = round(clock.get_fps(), 2)

    # Render text
    paused_text = info_font.render(f"Paused" if paused else "Playing", True, pygame.Color("white"))
    fps_text = info_font.render(f"FPS: {fps}", True, pygame.Color("white"))
    particle_count_text = info_font.render(f"Particles: {len(particles)}", True, pygame.Color("white"))
    brush_size_text = info_font.render(f"Brush size: {brushSize}", True, pygame.Color("white"))

    # Display text on screen
    screen.blit(paused_text, (10, window_size[1] - 90))
    screen.blit(fps_text, (10, window_size[1] - 70))
    screen.blit(particle_count_text, (10, window_size[1] - 50))
    screen.blit(brush_size_text, (10, window_size[1] - 30))
    pass


# Main simulation loop
def run_simulation():
    global paused, brushSize
    selectedType = 0
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:  # Space bar to pause/resume
                    paused = not paused
                elif event.key == K_UP:  # Increase brush size
                    brushSize = min(brushSize + 1, 9)  # Assuming a max brush size of 9
                elif event.key == K_DOWN:  # Decrease brush size
                    brushSize = max(brushSize - 1, 1)  # Assuming a min brush size of 1
                elif event.key == K_1:  # Select Sand
                    selectedType = 0
                elif event.key == K_2:  # Select Water
                    selectedType = 1
                elif event.key == K_3:  # Select Stone
                    selectedType = 2
                elif event.key == K_f:  # Assuming you want 'f' key to toggle fullscreen
                    if screen.get_flags() & pygame.FULLSCREEN:
                        # If already fullscreen, switch to windowed mode
                        pygame.display.set_mode(window_size, RESIZABLE)
                    else:
                        # If windowed, switch to fullscreen
                        pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                elif event.type == pygame.VIDEORESIZE:
                    # Update the window size when the window is resized
                    window_size = (display_info.current_w, display_info.current_h)
                    screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
            elif event.type == MOUSEBUTTONDOWN:
                add_particles(*pygame.mouse.get_pos(), event.button, selectedType)

        # Update and display simulation
        if not paused:
            update_simulation()

        display_info()

        # Flip the display
        pygame.display.flip()

        clock.tick(60)


if __name__ == "__main__":
    run_simulation()
