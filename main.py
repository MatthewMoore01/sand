import pygame
import random
import sys


class SandSimulation:
    def __init__(self, width, height, square_size):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Array Visualization")
        self.w = square_size
        self.cols = int(width / self.w)
        self.rows = int(height / self.w)
        self.grid = self.make_2d_array(self.cols, self.rows)
        self.velocity_grid = self.make_2d_array(self.cols, self.rows)
        self.hueValue = 50
        self.gravity = 1
        self.particle_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.hue_start = 20  # Start of the hue range

    def make_2d_array(self, cols, rows):
        return [[0 for _ in range(rows)] for _ in range(cols)]

    def within_cols(self, i):
        return 0 <= i < self.cols

    def within_rows(self, j):
        return 0 <= j < self.rows

    def erase_particles(self, mouse_col, mouse_row, matrix=2):
        extent = matrix // 2
        for i in range(-extent, extent + 1):
            for j in range(-extent, extent + 1):
                col = mouse_col + i
                row = mouse_row + j
                if self.within_cols(col) and self.within_rows(row):
                    self.grid[col][row] = 0  # Set the cell to 0 to erase the particle
                    self.velocity_grid[col][row] = 0  # Optionally reset the velocity grid as well

    def add_sand_particles(self, mouse_col, mouse_row, matrix=40):
        extent = matrix // 2
        for i in range(-extent, extent + 1):
            for j in range(-extent, extent + 1):
                if random.random() < 0.75:
                    col = mouse_col + i
                    row = mouse_row + j
                    if self.within_cols(col) and self.within_rows(row):
                        # Assign a random hue within a rolling window of 20 values
                        hue = random.uniform(self.hue_start, self.hue_start + 20)
                        self.grid[col][row] = hue
                        self.velocity_grid[col][row] = 1

        # Increment the start of the hue range
        self.hue_start += 0.3
        # Wrap around if the end of the hue range exceeds 100
        if self.hue_start > 80:
            self.hue_start = 20

    def draw_grid(self):
        # Clear the particle surface with a transparent fill before drawing the new frame.
        self.particle_surface.fill((0, 0, 0, 0))

        # Draw particles on the particle surface.
        for i in range(self.cols):
            for j in range(self.rows):
                state = self.grid[i][j]
                if state > 0:
                    hue = state
                    color = pygame.Color(0)
                    color.hsva = (30, 100, hue, 100)
                    # The particle is drawn as a rectangle here, but this could be optimized
                    # further based on the shape and size of your particles.
                    pygame.draw.rect(self.particle_surface, color, (i * self.w, j * self.w, self.w, self.w))

        # Blit the off-screen surface with all the particles onto the main screen.
        self.screen.blit(self.particle_surface, (0, 0))

    def update_particles(self):
        nextGrid = self.make_2d_array(self.cols, self.rows)
        nextVelocityGrid = self.make_2d_array(self.cols, self.rows)

        for i in range(self.cols):
            for j in range(self.rows):
                state = self.grid[i][j]
                if state > 0:
                    velocity = self.velocity_grid[i][j]
                    moved = False
                    newpos = int(j + velocity)

                    # Check within the bounds of the grid
                    for y in range(newpos, j, -1):
                        if 0 <= y < self.rows:
                            below = self.grid[i][y]
                            dir = 1 if random.random() < 0.5 else -1
                            i_dir_plus = i + dir
                            i_dir_minus = i - dir

                            # Check if the new positions are within bounds
                            if 0 <= i_dir_plus < self.cols:
                                belowA = self.grid[i_dir_plus][y]
                            else:
                                belowA = -1

                            if 0 <= i_dir_minus < self.cols:
                                belowB = self.grid[i_dir_minus][y]
                            else:
                                belowB = -1

                            if below == 0:
                                nextGrid[i][y] = state
                                nextVelocityGrid[i][y] = velocity + self.gravity
                                moved = True
                                break
                            elif belowA == 0:
                                nextGrid[i_dir_plus][y] = state
                                nextVelocityGrid[i_dir_plus][y] = velocity + self.gravity
                                moved = True
                                break
                            elif belowB == 0:
                                nextGrid[i_dir_minus][y] = state
                                nextVelocityGrid[i_dir_minus][y] = velocity + self.gravity
                                moved = True
                                break

                    if not moved and 0 <= j < self.rows:
                        nextGrid[i][j] = state
                        nextVelocityGrid[i][j] = min(velocity + self.gravity, self.rows - 1 - j)

        self.grid, self.velocity_grid = nextGrid, nextVelocityGrid

    def run(self):
        running = True
        clock = pygame.time.Clock()
        while running:
            self.screen.fill((0, 0, 0))  # Clear screen with black
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouseX, mouseY = pygame.mouse.get_pos()
                    mouseCol = mouseX // self.w
                    mouseRow = mouseY // self.w
                    if event.button == 1:  # Left mouse button adds particles
                        self.add_sand_particles(mouseCol, mouseRow)
                    elif event.button == 3:  # Right mouse button erases particles
                        self.erase_particles(mouseCol, mouseRow)
            mouse_pressed = pygame.mouse.get_pressed()
            if mouse_pressed[0]:  # If left mouse button is pressed and held
                mouseX, mouseY = pygame.mouse.get_pos()
                mouseCol = mouseX // self.w
                mouseRow = mouseY // self.w
                self.add_sand_particles(mouseCol, mouseRow)
            self.update_particles()
            self.draw_grid()
            pygame.display.flip()  # Update the display
            clock.tick(60)  # Limit to 60 frames per second


if __name__ == "__main__":
    sim = SandSimulation(800, 600, 4)  # Setup with desired window size and square size
    sim.run()
