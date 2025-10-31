import pygame, os

# Create folders if missing
os.makedirs(os.path.join("assets", "tiles"), exist_ok=True)

# Initialize pygame
pygame.init()

# Create surface (800x600 sky)
surface = pygame.Surface((800, 600))

# Simple blue gradient
for y in range(600):
    color = (135 - y//10, 206 - y//10, 235)  # light sky blue gradient
    pygame.draw.line(surface, color, (0, y), (800, y))

# Save to file
pygame.image.save(surface, os.path.join("assets", "tiles", "sky.png"))
print("✅ sky.png created successfully!")
