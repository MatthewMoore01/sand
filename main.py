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
        self.hueValue = 200
        self.gravity = 0.1
        self.update_counter = 0
        self.update_frequency = 5  # Update every 5 frames.
        self.particle_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    def make_2d_array(self, cols, rows):
        return [[0 for _ in range(rows)] for _ in range(cols)]

    def within_cols(self, i):
        return 0 <= i < self.cols

    def within_rows(self, j):
        return 0 <= j < self.rows

    def erase_particles(self, mouse_col, mouse_row, matrix=2):
        extent = matrix // 2
        #for i in range(-extent, extent + 1):
            #for j in range(-extent, extent + 1):
        col = mouse_col + 1
        row = mouse_row + 1
        if self.within_cols(col) and self.within_rows(row):
            self.grid[col][row] = 0  # Set the cell to 0 to erase the particle
            self.velocity_grid[col][row] = 0  # Optionally reset the velocity grid as well

    def add_sand_particles(self, mouse_col, mouse_row, matrix=5):
        extent = matrix // 2
        for i in range(-extent, extent + 1):
            for j in range(-extent, extent + 1):
                if random.random() < 0.75:
                    col = mouse_col + i
                    row = mouse_row + j
                    if self.within_cols(col) and self.within_rows(row):
                        self.grid[col][row] = self.hueValue
                        self.velocity_grid[col][row] = 1
        self.hueValue += 0.5
        if self.hueValue > 360:
            self.hueValue = 0

    def draw_grid(self):
        # Clear the particle surface at the start of each draw call
        self.particle_surface.fill((0, 0, 0, 0))  # Use a fully transparent fill

        # Draw particles on the particle surface
        for i in range(self.cols):
            for j in range(self.rows):
                if self.grid[i][j] > 0:
                    color = pygame.Color(0)
                    color.hsva = (self.grid[i][j], 100, 100, 100)
                    pygame.draw.rect(self.particle_surface, color, (i * self.w, j * self.w, self.w, self.w))

        # After drawing all particles, blit the particle surface to the main screen
        self.screen.blit(self.particle_surface, (0, 0))

    def update_particles(self):
        nextGrid = self.make_2d_array(self.cols, self.rows)
        nextVelocityGrid = self.make_2d_array(self.cols, self.rows)

        for i in range(self.cols):
            for j in range(self.rows):
                state = self.grid[i][j]
                velocity = self.velocity_grid[i][j]
                moved = False
                if state > 0:
                    newpos = int(j + velocity)
                    for y in range(newpos, j, -1):
                        if y < self.rows:  # Ensure we're not going out of bounds
                            below = self.grid[i][y]
                            dir = 1 if random.random() < 0.5 else -1
                            belowA = self.grid[i + dir][y] if self.within_cols(i + dir) else -1
                            belowB = self.grid[i - dir][y] if self.within_cols(i - dir) else -1

                            if below == 0:
                                nextGrid[i][y] = state
                                nextVelocityGrid[i][y] = velocity + self.gravity
                                moved = True
                                break
                            elif belowA == 0:
                                nextGrid[i + dir][y] = state
                                nextVelocityGrid[i + dir][y] = velocity + self.gravity
                                moved = True
                                break
                            elif belowB == 0:
                                nextGrid[i - dir][y] = state
                                nextVelocityGrid[i - dir][y] = velocity + self.gravity
                                moved = True
                                break

                if state > 0 and not moved:
                    # Ensure we're not assigning out of bounds
                    if j < self.rows:
                        nextGrid[i][j] = self.grid[i][j]
                        nextVelocityGrid[i][j] = min(
                            self.velocity_grid[i][j] + self.gravity, self.rows - 1 - j
                        )

        self.grid, self.velocity_grid = nextGrid, nextVelocityGrid

    def run(self):
        running = True
        clock = pygame.time.Clock()
        while running:
            self.screen.fill((0, 0, 0))  # Clear screen with black
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            mouse_pressed = pygame.mouse.get_pressed()
            mouseX, mouseY = pygame.mouse.get_pos()
            mouseCol = mouseX // self.w
            mouseRow = mouseY // self.w
            if mouse_pressed[0]:  # If left mouse button is pressed
                self.add_sand_particles(mouseCol, mouseRow)
            elif event.type == pygame.MOUSEBUTTONDOWN:  # If right mouse button is pressed, act as an eraser
                self.erase_particles(mouseCol, mouseRow)
            self.update_counter += 1
            if self.update_counter >= self.update_frequency:
                self.update_particles()
                self.update_counter = 0

            self.draw_grid()
            pygame.display.flip()  # Update the display
            clock.tick(60)  # Limit to 60 frames per second


if __name__ == "__main__":
    sim = SandSimulation(800, 600, 5)  # Setup with desired window size and square size
    sim.run()
