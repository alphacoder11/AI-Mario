import pygame
import math

class Enemy:
    def __init__(self, pos, params):
        self.rect = pygame.Rect(pos[0], pos[1], 32, 44)
        self.health = 2
        self.facing_right = True
        self.speed = params.get('speed', 48)
        self.detection_range = params.get('detection_range', 180)
        self.hit_timer = 0

    def update(self, platforms, player, dt, cam_x):
        pass

    def draw(self, surface, cam_x):
        px = self.rect.x - cam_x
        base_color = (80, 180, 50) if self.health == 2 else (180, 70, 40)
        if self.hit_timer > 0:
            color = (255, 230, 230)
        else:
            color = base_color
        pygame.draw.rect(surface, color, (px, self.rect.y, self.rect.width, self.rect.height))
        pygame.draw.circle(surface, (255, 255, 255), (px + (22 if self.facing_right else 10), self.rect.y + 9), 5)

class Patroller(Enemy):
    def __init__(self, pos, params):
        super().__init__(pos, params)
        self.dir = 1
        self.state = 'patrol'

    def update(self, platforms, player, dt, cam_x):
        self.rect.x += int(self.dir * self.speed * dt)
        edge_hit = True
        test_rect = self.rect.move(self.dir * 2, 12)
        for plat in platforms:
            rect = plat[0] if isinstance(plat, tuple) else plat
            if isinstance(rect, pygame.Rect) and test_rect.colliderect(rect):
                edge_hit = False
                break
        if edge_hit:
            self.dir *= -1
            self.facing_right = not self.facing_right
        if self.hit_timer > 0:
            self.hit_timer = max(0, self.hit_timer - dt)

class Chaser(Enemy):
    def __init__(self, pos, player, params):
        super().__init__(pos, params)
        self.player = player
        self.state = 'idle'

    def update(self, platforms, player, dt, cam_x):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist < self.detection_range:
            self.state = 'chase'
        else:
            self.state = 'idle'
        if self.state == 'chase':
            dir = 1 if dx > 0 else -1
            self.rect.x += int(dir * self.speed * dt)
            self.facing_right = dir == 1
        else:
            self.rect.x += int(math.sin(pygame.time.get_ticks() * 0.002) * 2)
        if self.hit_timer > 0:
            self.hit_timer = max(0, self.hit_timer - dt)
