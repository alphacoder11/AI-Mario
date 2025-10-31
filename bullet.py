import pygame

class Bullet:
    def __init__(self, pos, facing_right):
        self.rect = pygame.Rect(pos[0], pos[1], 18, 8)
        self.vel_x = 420 if facing_right else -420
        self.lifetime = 1.1
        self.last_camera_x = 0

    def update(self, dt):
        self.rect.x += int(self.vel_x * dt)
        self.lifetime -= dt

    def draw(self, surface, cam_x):
        bx = self.rect.x - cam_x
        pygame.draw.rect(surface, (60, 60, 230), (bx, self.rect.y, self.rect.width, self.rect.height))
