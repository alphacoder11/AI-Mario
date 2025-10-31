import pygame, os

os.makedirs("assets/tiles", exist_ok=True)
pygame.init()

# Enemy P — green patroller
enemy_p = pygame.Surface((32, 32), pygame.SRCALPHA)
enemy_p.fill((0, 200, 0))
pygame.draw.circle(enemy_p, (0, 100, 0), (16, 16), 14)
pygame.image.save(enemy_p, "assets/tiles/enemy_p.png")

# Enemy C — red chaser
enemy_c = pygame.Surface((32, 32), pygame.SRCALPHA)
enemy_c.fill((200, 0, 0))
pygame.draw.circle(enemy_c, (150, 0, 0), (16, 16), 14)
pygame.image.save(enemy_c, "assets/tiles/enemy_c.png")

print("✅ Enemies created in assets/tiles/")
