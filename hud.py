import pygame

class HUD:
    def __init__(self, width):
        self.width = width
        self.font = pygame.font.Font(None, 38)
        self.large_font = pygame.font.Font(None, 50)
        self.small_font = pygame.font.Font(None, 22)

    def draw(self, surface, score, lives, level, show_autoplayer):
        pygame.draw.rect(surface, (30, 30, 30), (0, 0, self.width, 43))
        tscore = self.font.render(f"Score: {score}", True, (230, 210, 90))
        tlives = self.font.render(f"Lives: {lives}", True, (210, 40, 60))
        tlevel = self.font.render(f"Level: {level}", True, (80, 180, 220))
        surface.blit(tscore, (18, 8))
        surface.blit(tlives, (200, 8))
        surface.blit(tlevel, (350, 8))
        if show_autoplayer:
            bot_mode = self.large_font.render("AutoPlayer: ON (F1)", True, (130,230,100))
        else:
            bot_mode = self.large_font.render("AutoPlayer: OFF (F1)", True, (180,110,100))
        surface.blit(bot_mode, (500, 7))
        hint = self.small_font.render("A/D move  W/Space jump  J/K shoot  P pause", True, (200, 200, 200))
        surface.blit(hint, (500, 24))
