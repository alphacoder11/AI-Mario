import json
import os

class AdaptiveAI:
    def __init__(self, filename):
        self.filename = filename
        self.params = {
            'speed': 48,
            'detection_range': 180
        }
        self.score_samples = []
        if self.filename and os.path.exists(self.filename):
            self.load()

    def track_score(self, score):
        if len(self.score_samples) < 50:
            self.score_samples.append(score)
        else:
            self.score_samples = self.score_samples[-49:] + [score]

    def update_enemies(self, enemies):
        avg_score = (sum(self.score_samples) / len(self.score_samples)) if self.score_samples else 0
        if avg_score > 500:
            self.params['speed'] = min(self.params['speed'] + 0.12, 88)
            self.params['detection_range'] = min(self.params['detection_range'] + 2.5, 340)
            for enemy in enemies:
                enemy.speed = self.params['speed']
                enemy.detection_range = self.params['detection_range']

    def get_params(self):
        return self.params

    def save(self):
        if not self.filename:
            return
        with open(self.filename, 'w') as f:
            json.dump(self.params, f)

    def load(self):
        if not self.filename:
            return
        with open(self.filename, 'r') as f:
            self.params = json.load(f)

class AutoPlayer:
    @staticmethod
    def control(player, level, enemies, coins, bullets, sound_jump, sound_shoot):
        close_ground = any(
            (plat[0] if isinstance(plat, tuple) else plat).colliderect(player.rect.move(30, 25))
            for plat in level.platforms
        )
        danger = any(
            enemy.rect.colliderect(player.rect.inflate(50, 15)) for enemy in enemies
        )
        move_right = True
        move_left = False
        jump = False
        shoot = danger
        if not close_ground or player.rect.bottom > 470:
            jump = True
        nearest_coin = None
        min_dist = 9999
        for coin in coins:
            if coin['taken']:
                continue
            cx, cy = coin['rect'].center
            dist = abs(cx - player.rect.centerx)
            if dist < min_dist:
                min_dist = dist
                nearest_coin = coin
        if nearest_coin and nearest_coin['rect'].centerx < player.rect.centerx:
            move_left = True
            move_right = False
        player.handle_input(move_left, move_right, jump, shoot, bullets, sound_jump, sound_shoot)
