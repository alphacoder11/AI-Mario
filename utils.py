import json
import pygame

def clamp(val, lo, hi):
    return max(lo, min(hi, val))

def load_highscore(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f).get('highscore', 0)
    except Exception:
        return 0

def save_highscore(filename, score):
    try:
        with open(filename, 'w') as f:
            json.dump({'highscore': score}, f)
    except Exception:
        pass

def play_sound(sound_file):
    try:
        return pygame.mixer.Sound(sound_file)
    except Exception:
        return None
