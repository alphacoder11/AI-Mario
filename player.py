import pygame
from bullet import Bullet
from utils import clamp

GRAVITY = 1200
JUMP_VELOCITY = 500
MAX_FALL_SPEED = 900

class Player:
    def __init__(self, spawn_pos, screen_height):
        self.rect = pygame.Rect(spawn_pos[0], spawn_pos[1], 32, 48)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.jumping = False
        self.jump_timer = 0
        self.facing_right = True
        self.screen_height = screen_height
        self.shoot_cooldown = 0.0
        self.invuln_timer = 0.0
        # Static sprite (no run animation)
        self.sprite_right = None
        self.sprite_left = None
        try:
            img = pygame.image.load("assets/tiles/player.png").convert_alpha()
            img = pygame.transform.smoothscale(img, (self.rect.width, self.rect.height))
            self.sprite_right = img
            self.sprite_left = pygame.transform.flip(img, True, False)
        except Exception:
            self.sprite_right = None
            self.sprite_left = None

    def handle_input(self, move_left, move_right, jump, shoot, bullets, sound_jump, sound_shoot):
        if move_left:
            self.vel_x -= 18
            self.facing_right = False
        if move_right:
            self.vel_x += 18
            self.facing_right = True

        # 🦘 Jump
        if jump:
            if self.on_ground:
                self.jumping = True
                self.jump_timer = 0.13
                self.vel_y = -JUMP_VELOCITY
                if sound_jump:
                    sound_jump.play()
        if self.jumping and jump:
            self.jump_timer -= 1 / 60
            if self.jump_timer > 0:
                self.vel_y -= GRAVITY * 0.012
            else:
                self.jumping = False
        if not jump:
            self.jumping = False

        # 🔫 Shoot
        if shoot and self.shoot_cooldown <= 0:
            bx = self.rect.centerx + (28 if self.facing_right else -20)
            bullets.append(Bullet((bx, self.rect.centery), self.facing_right))
            self.shoot_cooldown = 0.28
            if sound_shoot:
                sound_shoot.play()

    def update(self, platforms, dt):
        # Cooldowns
        if self.shoot_cooldown > 0:
            self.shoot_cooldown = max(0.0, self.shoot_cooldown - dt)
        if self.invuln_timer > 0:
            self.invuln_timer = max(0.0, self.invuln_timer - dt)

        # Horizontal movement
        self.vel_x *= 0.86
        self.rect.x += int(self.vel_x * dt)

        # Vertical movement
        self.vel_y += GRAVITY * dt
        self.vel_y = clamp(self.vel_y, -JUMP_VELOCITY, MAX_FALL_SPEED)
        self.rect.y += int(self.vel_y * dt)

        # 🧱 Collision detection
        self.on_ground = False
        for plat in platforms:
            rect = plat[0] if isinstance(plat, tuple) else plat
            if not isinstance(rect, pygame.Rect):
                continue

            if self.rect.colliderect(rect):
                # Landing on platform
                if self.vel_y > 0:
                    self.rect.bottom = rect.top
                    self.vel_y = 0
                    self.on_ground = True
                # Hitting ceiling
                elif self.vel_y < 0:
                    self.rect.top = rect.bottom
                    self.vel_y = 0

        # Animate
        self._animate(dt)

    def draw(self, surface, cam_x):
        px = self.rect.x - cam_x
        if self.sprite_right:
            sprite = self.sprite_right if self.facing_right else self.sprite_left
            surface.blit(sprite, (px, self.rect.y))
        else:
            color = (220, 60, 30) if self.invuln_timer <= 0 else (220, 160, 160)
            pygame.draw.rect(surface, color, (px, self.rect.y, self.rect.width, self.rect.height))
            eye_color = (255, 255, 255) if self.facing_right else (30, 30, 30)
            pygame.draw.circle(surface, eye_color,
                               (px + 22 if self.facing_right else px + 10, self.rect.y + 12), 4)
            pygame.draw.rect(surface, (40, 40, 40), (px + 7, self.rect.y + 33, 18, 8), 2)

    def respawn(self, spawn_pos):
        self.rect.x, self.rect.y = spawn_pos
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False

    # Internal helpers
    def _load_sprites(self):
        # Try sprite sheet first
        try:
            sheet = pygame.image.load("assets/tiles/RunnerRex_32x48px.png").convert_alpha()
            sw, sh = sheet.get_size()
            tw, th = 32, 48
            cols = max(1, sw // tw)
            rows = max(1, sh // th)
            frames = []
            for y in range(rows):
                for x in range(cols):
                    rect = pygame.Rect(x * tw, y * th, tw, th)
                    sub = sheet.subsurface(rect).copy()
                    frames.append(sub)
            # Heuristic: first frame idle, next 4 run, a later frame for jump if available
            if frames:
                self.frames_idle = [frames[0]]
                if len(frames) >= 5:
                    self.frames_run = frames[1:5]
                    self.jump_frame = frames[5] if len(frames) > 5 else frames[1]
                else:
                    # If only one frame exists, create procedural run/jump frames by rotating and bobbing
                    base = pygame.transform.smoothscale(frames[0], (self.rect.width, self.rect.height))
                    self.frames_idle = [base]
                    self.frames_run = [
                        pygame.transform.rotate(base, -15),
                        base,
                        pygame.transform.rotate(base, 15),
                        base,
                    ]
                    self.jump_frame = pygame.transform.rotate(base, -18)
        except Exception:
            pass
        # Fallback single sprite
        if not self.frames_idle:
            try:
                img = pygame.image.load("assets/tiles/player.png").convert_alpha()
                img = pygame.transform.smoothscale(img, (self.rect.width, self.rect.height))
                self.sprite_right = img
                self.sprite_left = pygame.transform.flip(img, True, False)
                # Also construct simple procedural frames from this image
                base = img
                self.frames_idle = [base]
                self.frames_run = [
                    pygame.transform.rotate(base, -10),
                    base,
                    pygame.transform.rotate(base, 10),
                    base,
                ]
                self.jump_frame = pygame.transform.rotate(base, -12)
            except Exception:
                self.sprite_right = None
                self.sprite_left = None

    def _animate(self, dt):
        # No-op (animation disabled)
        return

    def _current_frame(self):
        # airborne overrides
        return None
