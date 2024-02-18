import pygame
import random
import sys


class SandSimulation:
    def __init__(self, square_size):
        pygame.init()
        pygame.font.init()  # Initialize the font module
        self.font = pygame.font.SysFont(None, 24)  # Choose the default system font and set the size
        display_info = pygame.display.Info()
        self.world_width = display_info.current_w
        self.world_height = display_info.current_h

        # Set the window size to some fraction of the screen size for windowed mode
        # or you can use the full screen size for full screen mode.
        width = self.world_width // 2
        height = self.world_height // 2

        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption("Array Visualization")
        self.w = square_size

        # Define a viewport rect that represents the currently visible area of the world
        self.viewport = pygame.Rect(0, 0, width, height)

        # Create a grid that represents the entire world
        self.cols = int(self.world_width / self.w)
        self.rows = int(self.world_height / self.w)
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
        # Clear the screen with a black fill before drawing the new frame.
        self.screen.fill((0, 0, 0))

        # Calculate the visible range based on the viewport
        visible_start_col = max(0, self.viewport.left // self.w)
        visible_end_col = min(self.cols, (self.viewport.right // self.w) + 1)
        visible_start_row = max(0, self.viewport.top // self.w)
        visible_end_row = min(self.rows, (self.viewport.bottom // self.w) + 1)

        # Pre-create a color object to avoid creating a new one for each particle
        particle_color = pygame.Color(0)

        # Iterate only over the visible particles
        for col in range(visible_start_col, visible_end_col):
            for row in range(visible_start_row, visible_end_row):
                state = self.grid[col][row]
                if state > 0:
                    # Update the color's hue value
                    particle_color.hsva = (30, 100, state, 100)
                    screen_x = (col - visible_start_col) * self.w
                    screen_y = (row - visible_start_row) * self.w
                    pygame.draw.rect(self.screen, particle_color, (screen_x, screen_y, self.w, self.w))

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
        scroll_speed = 10  # Adjust as needed for the scrolling speed

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    # Adjust the viewport size without changing the world size
                    new_width, new_height = event.w, event.h
                    old_height = self.viewport.height
                    self.viewport.size = (new_width, new_height)

                    # Adjust the vertical position of the viewport to keep the floor at the bottom
                    height_difference = new_height - old_height
                    self.viewport.bottom += height_difference

                    # Ensure the viewport does not go beyond the world's top boundary
                    self.viewport.top = max(0, self.viewport.top)
                    self.viewport.bottom = min(self.world_height, self.viewport.bottom)

                    self.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
                    # Recreate the particle surface if necessary or resize it

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouseX, mouseY = pygame.mouse.get_pos()
                    mouseCol = (mouseX + self.viewport.left) // self.w
                    mouseRow = (mouseY + self.viewport.top) // self.w
                    if event.button == 1:  # Left mouse button adds particles
                        self.add_sand_particles(mouseCol, mouseRow)
                    elif event.button == 3:  # Right mouse button erases particles
                        self.erase_particles(mouseCol, mouseRow)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.viewport.x = max(self.viewport.x - scroll_speed, 0)  # Scroll left
            if keys[pygame.K_RIGHT]:
                self.viewport.x = min(self.viewport.x + scroll_speed, self.world_width - self.viewport.width)  # Scroll right
            # Add more controls if you want to scroll vertically as well

            mouse_pressed = pygame.mouse.get_pressed()
            if mouse_pressed[0]:  # If left mouse button is pressed and held
                mouseX, mouseY = pygame.mouse.get_pos()
                mouseCol = (mouseX + self.viewport.left) // self.w
                mouseRow = (mouseY + self.viewport.top) // self.w
                self.add_sand_particles(mouseCol, mouseRow)

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
    sim = SandSimulation(4)  # Pass the square size directly
    sim.run()
