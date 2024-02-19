import pygame
import numpy as np
from pygame.locals import *
from noise import pnoise2  # You might need to adjust this import based on your noise function
import random

# Global variables for the simulation
gridSize = 200  # Adjust based on your simulation needs
grid = [None] * (gridSize * gridSize)
particles = []

class Particle:
    def __init__(self, options):
        self.offset = options['offset']
        self.position = options['position']
        self.colorOffset = int(noise(pygame.time.get_ticks()))
        self.color = [0, 0, 0]  # Default color, to be overridden by subclasses

    def update(self, window_size, screen):
        newPos = self.findNewPosition(self.position['x'], self.position['y'])
        if newPos:
            self.replaceCurrentPosition()
            self.moveToNewPosition(newPos)
        self.display(window_size, screen)

    def replaceCurrentPosition(self):
        grid[self.offset] = None

    def moveToNewPosition(self, newPos):
        self.position = newPos
        self.offset = newPos['offset']
        grid[self.offset] = self

    def display(self, window_size, screen):
        # Assuming self.position is in grid coordinates, scale to screen coordinates
        screen_x = int(self.position['x'] / gridSize * window_size[0])
        screen_y = int(self.position['y'] / gridSize * window_size[1])
        radius = 5  # Radius of the particle circle

        # Draw the particle as a circle at the scaled screen position
        pygame.draw.circle(screen, self.color, (screen_x, screen_y), radius)

    def remove(self):
        self.replaceCurrentPosition()
        particles.remove(self)

# Function to create noise-based color offset
def noise(frame_count):
    return pnoise2(frame_count * 0.1, 0) * 100

class Sand(Particle):
    def __init__(self, options):
        super().__init__(options)
        self.name = 'Sand'
        self.value = 255
        self.color = [149, 113, 95]  # Default sand color
        self.wet = False

    def findNewPosition(self, x, y): # Very broken
        potential_positions = [
            {'x': x, 'y': y + 1},  # Directly below
            {'x': x + 1, 'y': y + 1},  # Diagonally right below
            {'x': x - 1, 'y': y + 1}  # Diagonally left below
        ]
        for pos in potential_positions:
            offset = pos['y'] * gridSize + pos['x']
            if pos['y'] < gridSize and pos['x'] < gridSize and pos['x'] >= 0:
                if not grid[offset] or grid[offset].name == "Water":
                    return {'x': pos['x'], 'y': pos['y'], 'offset': offset}
        current_offset = y * gridSize + x

        if grid[current_offset] and grid[current_offset].name == "Water":
            self.wet = True
        else:
            self.wet = False

        return None  # Return None if no new position is found

    def display(self, window_size, screen):
        # Adjust color if wet
        display_color = self.color.copy()  # Copy the color so we don't modify the original
        if self.wet:
            # Darken the color by 35%
            display_color = [int(c * 0.65) for c in display_color]

        # Now, call the display method of the base class with the modified color
        original_color = self.color  # Store the original color
        self.color = display_color  # Temporarily set the color to the display color
        super().display(window_size, screen)  # Call the display method of the base class
        self.color = original_color  # Reset the color to the original after drawing


class Water(Particle):
    def __init__(self, options):
        super().__init__(options)
        self.name = 'Water'
        self.value = 254
        self.color = [10, 10, 250]  # Default water color

    def findNewPosition(self, x, y):
        potential_positions = [
            {'x': x, 'y': y + 1},  # Directly below
            {'x': x + 1, 'y': y + 1},  # Diagonally right below
            {'x': x - 1, 'y': y + 1},  # Diagonally left below
            {'x': x + 1, 'y': y},  # Right
            {'x': x - 1, 'y': y}   # Left
        ]
        for pos in potential_positions:
            offset = pos['y'] * gridSize + pos['x']
            if pos['y'] < gridSize and pos['x'] < gridSize and pos['x'] >= 0:
                if not grid[offset]:
                    return {'x': pos['x'], 'y': pos['y'], 'offset': offset}
        return None

    def display(self, window_size, screen):
        super().display(window_size, screen)  # Use the base class method to display


class Stone(Particle):
    def __init__(self, options):
        super().__init__(options)
        self.name = 'Stone'
        self.value = 253
        self.color = [125, 125, 125]  # Default stone color
        self.colorOffset = int((random.random() * 2 - 1) * 50)

    def findNewPosition(self, x, y):
        return None  # Stones do not move

    def display(self, window_size, screen):
        # Adjust the stone color slightly for visual variety
        self.color = [
            max(min(255, self.color[0] + self.colorOffset), 0),
            max(min(255, self.color[1] + self.colorOffset), 0),
            max(min(255, self.color[2] + self.colorOffset), 0)
        ]
        super().display(window_size, screen)  # Call the base class display method to show the stone