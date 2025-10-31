import pygame
import os

TILE_SIZE = 64

class Level:
    def __init__(self, filename):
        self.filename = filename
        self.platforms = []
        self.enemy_spawns = []
        self.coin_spawns = []
        self.player_spawn = (64, 64)
        self.width = 0
        self.height = 0

        self.colors = {
            '#': (139, 69, 19),   # Brown - ground/platform
            'C': (255, 215, 0),   # Gold - coin
            '@': (200, 0, 0),     # Red - player spawn
            'E': (0, 0, 255),     # Blue - enemy
            '$': (0, 255, 0),     # Green - bonus or obstacle
            'P': (180, 180, 255), # Light blue - special platform
        }

        self.load_level()

    def load_level(self):
        with open(self.filename, "r") as f:
            lines = [line.rstrip("\n") for line in f.readlines()]

        self.height = len(lines)
        self.width = max(len(line) for line in lines)

        for y, line in enumerate(lines):
            for x, ch in enumerate(line):
                world_x = x * TILE_SIZE
                world_y = y * TILE_SIZE
                rect = pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE)

                if ch == "#":
                    self.platforms.append((rect, ch))
                elif ch == "C":
                    self.coin_spawns.append((world_x, world_y))
                elif ch == "@":
                    self.player_spawn = (world_x, world_y)
                elif ch == "E":
                    # Map legacy 'E' to Chaser type
                    self.enemy_spawns.append(("C", (world_x, world_y)))
                elif ch == "$":
                    self.platforms.append((rect, ch))
                elif ch == "P":
                    # Keep special platform visual, also treat as a Patroller spawn
                    self.platforms.append((rect, ch))
                    self.enemy_spawns.append(("P", (world_x, world_y)))

    def draw(self, surface, cam_x):
        for rect, symbol in self.platforms:
            color = self.colors.get(symbol, (120, 120, 120))
            pygame.draw.rect(surface, color,
                             (rect.x - cam_x, rect.y, rect.width, rect.height))

        # Draw coins
        for (x, y) in self.coin_spawns:
            pygame.draw.circle(surface, self.colors["C"], (x - cam_x + 32, y + 32), 12)

        # Draw enemies (editor-style markers). Support typed and legacy formats.
        for item in self.enemy_spawns:
            if isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], str):
                _, (x, y) = item
            else:
                x, y = item
            pygame.draw.rect(surface, self.colors["E"], (x - cam_x + 8, y + 16, 48, 48))
