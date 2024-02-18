import pygame
import random
import sys


class ParticleType:
    EMPTY = 0
    SAND = 1
    STONE = 2
    WATER = 3


PARTICLE_HUES = {
    ParticleType.SAND: 30,  # Hue for sand
    ParticleType.STONE: 40,  # Hue for stone
    ParticleType.WATER: 90,  # Hue for water
}

PARTICLE_LIGHT = {
    ParticleType.SAND: 100,  # Lightness for sand
    ParticleType.STONE: 50,   # Lightness for stone
    ParticleType.WATER: 100,  # Lightness for water
}

PARTICLE_BRUSH = {
    ParticleType.SAND: 50,  # Brush size for sand
    ParticleType.STONE: 10,  # Brush size for stone
    ParticleType.WATER: 10,  # Brush size for water
}



class SandSimulation:
    def __init__(self, square_size):
        pygame.init()
        pygame.font.init()  # Initialize the font module
        self.font = pygame.font.SysFont(None, 24)  # Choose the default system font and set the size
        display_info = pygame.display.Info()
        self.world_width = display_info.current_w
        self.world_height = display_info.current_h
        self.active_particles = set()

        # Set the window size to some fraction of the screen size for windowed mode
        # or you can use the full screen size for full screen mode.
        width = self.world_width
        height = self.world_height - 60

        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption("Array Visualization")
        self.w = square_size

        # Define a viewport rect that represents the currently visible area of the world
        self.viewport = pygame.Rect(0, 0, width, height)

        # Create a grid that represents the entire world
        self.cols = int(width / self.w)
        self.rows = int(height / self.w)
        self.grid = self.make_2d_array(self.cols, self.rows)
        self.velocity_grid = self.make_2d_array(self.cols, self.rows)
        self.gravity = 0.001
        self.particle_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.sat_start = 20

    def make_2d_array(self, cols, rows):
        return [[(ParticleType.EMPTY, 0) for _ in range(rows)] for _ in range(cols)]

    def within_cols(self, i):
        return 0 <= i < self.cols

    def within_rows(self, j):
        return 0 <= j < self.rows

    def erase_particles(self, mouse_col, mouse_row, particle_type, matrix=4):
        extent = matrix // 2
        for i in range(-extent, extent + 1):
            for j in range(-extent, extent + 1):
                col = mouse_col + i
                row = mouse_row + j
                if self.within_cols(col) and self.within_rows(row):
                    self.grid[col][row] = (ParticleType.EMPTY, 0)  # Update to use the tuple format for consistency
                    self.velocity_grid[col][row] = 0
                    self.active_particles.discard((col, row))

                    # Activate surrounding particles if they can potentially move
                    if particle_type == ParticleType.SAND or ParticleType.WATER:
                        for dy in [-1, 0, 1]:  # Check the row above, same row, and below
                            for dx in [-1, 0, 1]:  # Check left, same column, and right
                                adj_col, adj_row = col + dx, row + dy
                                if self.within_bounds(adj_col, adj_row) and self.grid[adj_col][adj_row][
                                    0] != ParticleType.EMPTY:
                                    self.active_particles.add((adj_col, adj_row))

    def add_particle(self, mouse_col, mouse_row, particle_type):
        matrix = PARTICLE_BRUSH.get(particle_type, 30)
        extent = matrix // 2
        for i in range(-extent, extent + 1):
            for j in range(-extent, extent + 1):
                col = mouse_col + i
                row = mouse_row + j
                if (col, row) not in self.active_particles and self.within_cols(col) and self.within_rows(row):
                    sat = random.uniform(self.sat_start, self.sat_start + 20)
                    self.grid[col][row] = (particle_type, sat)  # Store particle type and sat in a tuple

                    # Set initial velocity based on particle type
                    initial_velocity = 1 if particle_type == ParticleType.SAND else 1
                    self.velocity_grid[col][row] = initial_velocity

                    # Add to active particles if it's sand, since stone doesn't move
                    self.active_particles.add((col, row))

        # Increment the start of the sat range
        self.sat_start += 1
        # Wrap around if the end of the sat range exceeds 100
        if self.sat_start > 80:
            self.sat_start = 20

    def draw_grid(self):
        # Clear the screen with a black fill before drawing the new frame.
        self.screen.fill((0, 0, 0))

        # Calculate the visible range based on the viewport
        visible_start_col = max(0, self.viewport.left // self.w)
        visible_end_col = min(self.cols, (self.viewport.right // self.w) + 1)
        visible_start_row = max(0, self.viewport.top // self.w)
        visible_end_row = min(self.rows, (self.viewport.bottom // self.w) + 1)

        # Iterate only over the visible particles
        for col in range(visible_start_col, visible_end_col):
            for row in range(visible_start_row, visible_end_row):
                particle_type, saturation = self.grid[col][row]
                if particle_type != ParticleType.EMPTY:
                    # Determine the hue based on particle type
                    hue = PARTICLE_HUES.get(particle_type)
                    light = PARTICLE_LIGHT.get(particle_type)
                    # Update the particle_color's hsva value
                    particle_color = pygame.Color(0)
                    particle_color.hsva = (hue, light, saturation, 100)

                    # Calculate the position to draw the rectangle on the screen
                    screen_x = (col - visible_start_col) * self.w
                    screen_y = (row - visible_start_row) * self.w
                    pygame.draw.rect(self.screen, particle_color, (screen_x, screen_y, self.w, self.w))

    def update_particles(self):
        nextGrid = self.make_2d_array(self.cols, self.rows)
        nextVelocityGrid = self.make_2d_array(self.cols, self.rows)
        new_active_particles = set()

        for col, row in self.active_particles:
            state = self.grid[col][row]
            particle_type, saturation = state
            directions = [1, -1] if random.random() < 0.5 else [-1, 1]

            moved = False  # Flag to track if the particle has moved

            # Sand specific logic for falling
            if particle_type == ParticleType.SAND:
                if row + 1 < self.rows and self.grid[col][row + 1][0] == ParticleType.EMPTY:
                    # Move sand down if the spot directly below is empty
                    nextGrid[col][row + 1] = state
                    nextVelocityGrid[col][row + 1] = self.gravity
                    new_active_particles.add((col, row + 1))
                    moved = True
                else:
                    # Try to move sand diagonally down if the spot directly below is not empty
                    for dir in directions:
                        adjacent_col = col + dir
                        if row + 1 < self.rows and self.within_cols(adjacent_col) and self.grid[adjacent_col][row + 1][
                            0] == ParticleType.EMPTY:
                            nextGrid[adjacent_col][row + 1] = state
                            nextVelocityGrid[adjacent_col][row + 1] = self.gravity
                            new_active_particles.add((adjacent_col, row + 1))
                            moved = True
                            break

            # Water specific logic for falling and spreading
            elif particle_type == ParticleType.WATER:
                moved = False
                # First, try moving down
                if row + 1 < self.rows and self.grid[col][row + 1][0] == ParticleType.EMPTY:
                    nextGrid[col][row + 1] = state
                    nextVelocityGrid[col][row + 1] = 0  # No gravity effect for water moving down
                    new_active_particles.add((col, row + 1))
                    moved = True
                else:
                    # Try to move water right if the spot directly below is not empty
                    if self.within_cols(col + 1) and self.grid[col + 1][row][0] == ParticleType.EMPTY:
                        nextGrid[col + 1][row] = state
                        nextVelocityGrid[col + 1][row] = self.gravity  # No gravity effect for water moving right
                        new_active_particles.add((col + 1, row))
                        moved = True
                    # If moving right is not possible, then try to move left
                    elif self.within_cols(col - 1) and self.grid[col - 1][row][0] == ParticleType.EMPTY:
                        nextGrid[col - 1][row] = state
                        nextVelocityGrid[col - 1][row] = self.gravity  # No gravity effect for water moving left
                        new_active_particles.add((col - 1, row))
                        moved = True

                # If water couldn't move down, right, or left, keep it in its current position
                if not moved:
                    nextGrid[col][row] = state
                    nextVelocityGrid[col][row] = 0
                    new_active_particles.add((col, row))

            # If the particle has not moved (either it's at the bottom or surrounded), keep it in its current position
            if not moved:
                nextGrid[col][row] = state
                nextVelocityGrid[col][row] = self.gravity if particle_type == ParticleType.SAND else 0
                new_active_particles.add((col, row))

        # Update the grid and active particles for the next iteration
        self.grid, self.velocity_grid = nextGrid, nextVelocityGrid
        self.active_particles = new_active_particles

    def run(self):
        running = True
        clock = pygame.time.Clock()
        scroll_speed = 10
        current_particle_type = ParticleType.SAND

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    # Adjust the viewport size without changing the world size
                    new_width, new_height = event.w, event.h
                    self.viewport.size = (new_width, new_height)
                    self.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouseX, mouseY = pygame.mouse.get_pos()
                    mouseCol = (mouseX + self.viewport.left) // self.w
                    mouseRow = (mouseY + self.viewport.top) // self.w
                    if event.button == 1:  # Left mouse button adds particles
                        self.add_particle(mouseCol, mouseRow, current_particle_type)
                    elif event.button == 3:  # Right mouse button erases particles
                        self.erase_particles(mouseCol, mouseRow, current_particle_type)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        current_particle_type = ParticleType.SAND
                    elif event.key == pygame.K_2:
                        current_particle_type = ParticleType.STONE
                    elif event.key == pygame.K_3:
                        current_particle_type = ParticleType.WATER

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.viewport.x = max(self.viewport.x - scroll_speed, 0)  # Scroll left
            if keys[pygame.K_RIGHT]:
                self.viewport.x = min(self.viewport.x + scroll_speed,
                                      self.world_width - self.viewport.width)  # Scroll right

            # Drawing everything
            self.update_particles()
            self.draw_grid()

            # Render the FPS text and blit it onto the screen
            fps = clock.get_fps()
            fps_text = self.font.render(f"FPS: {fps:.2f}", True, pygame.Color('white'))
            self.screen.blit(fps_text, (10, 10))  # Position the text in the top-left corner

            pygame.display.flip()  # Update the display
            clock.tick(60)  # Limit to 60 frames per second


if __name__ == "__main__":
    sim = SandSimulation(6)  # Pass the square size directly
    sim.run()
