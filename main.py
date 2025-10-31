import pygame
import sys
import os
import traceback
import random
import math
from player import Player
from enemy import Patroller, Chaser
from bullet import Bullet
from level import Level, TILE_SIZE
from hud import HUD
from ai import AdaptiveAI, AutoPlayer
from utils import load_highscore, save_highscore, play_sound, clamp
BACKGROUND_IMG = None


# Basic config
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
FPS = 60
DATA_DIR = 'data'
ASSETS_DIR = 'assets'
SOUND_DIR = os.path.join(ASSETS_DIR, 'sounds')

# Init pygame
# Be explicit about audio init to avoid rare freezes when no device/driver
is_audio_enabled = True
try:
    # Prefer a stable Windows driver; fallback is handled below
    if sys.platform.startswith('win') and 'SDL_AUDIODRIVER' not in os.environ:
        os.environ['SDL_AUDIODRIVER'] = 'directsound'
    pygame.mixer.pre_init(44100, -16, 2, 512)
except Exception:
    is_audio_enabled = False

pygame.init()
try:
    if is_audio_enabled and not pygame.mixer.get_init():
        pygame.mixer.init()
except Exception:
    is_audio_enabled = False

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AI Mario – Smart Platform Adventure")
clock = pygame.time.Clock()

# Load background image after display init; fall back to gradient if missing
try:
    BACKGROUND_IMG = pygame.image.load(os.path.join("assets", "tiles", "sky.png")).convert()
    # scale to fit window to avoid partial fills
    BACKGROUND_IMG = pygame.transform.smoothscale(BACKGROUND_IMG, (SCREEN_WIDTH, SCREEN_HEIGHT))
except Exception:
    BACKGROUND_IMG = None

# Utility: safe play_sound wrapper (play_sound may already be resilient)
def safe_play_sound(path):
    if not is_audio_enabled:
        return None
    try:
        return play_sound(path)
    except Exception:
        # fallback None if sound can't be loaded
        print(f"[warn] sound missing or failed to load: {path}")
        return None

sound_coin = safe_play_sound(os.path.join(SOUND_DIR, 'coin.wav'))
sound_jump = safe_play_sound(os.path.join(SOUND_DIR, 'jump.wav'))
sound_shoot = safe_play_sound(os.path.join(SOUND_DIR, 'shoot.wav'))

# Global sound state and helpers
is_muted = False
_BASE_MUSIC_VOL = 0.6
_BASE_SFX_VOL = 0.8

def apply_volume():
    vol = 0.0 if is_muted else _BASE_MUSIC_VOL
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(vol)
    except Exception:
        pass
    sfx_vol = 0.0 if is_muted else _BASE_SFX_VOL
    for s in (sound_coin, sound_jump, sound_shoot):
        try:
            if s:
                s.set_volume(sfx_vol)
        except Exception:
            pass

def toggle_mute():
    global is_muted
    is_muted = not is_muted
    apply_volume()

def get_sound_button_rect():
    return pygame.Rect(SCREEN_WIDTH - 56, 10, 46, 36)

def draw_sound_button(surface):
    # Simple speaker icon in top-right
    rect = get_sound_button_rect()
    bx, by, bw, bh = rect.x, rect.y, rect.width, rect.height
    pygame.draw.rect(surface, (0, 0, 0), rect, 2)
    # speaker
    sx = bx + 10
    sy = by + bh // 2
    pygame.draw.polygon(surface, (240, 240, 240), [(sx, sy-8), (sx+10, sy-8), (sx+18, sy-14), (sx+18, sy+14), (sx+10, sy+8), (sx, sy+8)])
    if is_muted:
        # draw X
        pygame.draw.line(surface, (220, 60, 60), (bx+28, by+8), (bx+bw-6, by+bh-8), 3)
        pygame.draw.line(surface, (220, 60, 60), (bx+bw-6, by+8), (bx+28, by+bh-8), 3)
    else:
        # sound waves
        pygame.draw.arc(surface, (240,240,240), (bx+24, by+6, 16, 12), 0.2, 3.0, 2)
        pygame.draw.arc(surface, (240,240,240), (bx+26, by+2, 22, 20), 0.2, 3.0, 2)
    return rect

WHITE = (255, 255, 255)
SKY = (120, 180, 240)

# --- Compact helpers (no behavior change) ---
def update_parallax(dt):
    for c in clouds:
        c['x'] -= c['speed'] * dt
        if c['x'] < -220:
            c['x'] = SCREEN_WIDTH + random.randint(10, 200)
            c['y'] = random.randint(20, SCREEN_HEIGHT // 2)
            c['scale'] = random.uniform(0.6, 1.4)
            c['speed'] = random.uniform(10, 30) * (0.6 + (1.6 - c['scale']))
    for b in birds:
        b['x'] -= b['speed'] * dt
        b['flap'] += dt * 8.0
        if b['x'] < -60:
            b['x'] = SCREEN_WIDTH + random.randint(50, 300)
            b['y'] = random.randint(80, SCREEN_HEIGHT // 2 + 80)
            b['speed'] = random.uniform(60, 120)
            b['flap'] = random.uniform(0, 6.28)

def draw_parallax(surface):
    # clouds
    for c in clouds:
        sx, sy = int(60 * c['scale']), int(30 * c['scale'])
        x, y = int(c['x']), int(c['y'])
        pygame.draw.ellipse(surface, (255, 255, 255), (x, y, sx, sy))
        pygame.draw.ellipse(surface, (255, 255, 255), (x + sx//3, y - sy//3, sx, sy))
        pygame.draw.ellipse(surface, (255, 255, 255), (x + sx//2, y, sx, sy))
    # birds
    for b in birds:
        x = int(b['x'])
        y = int(b['y'] + math.sin(b['flap']) * 6)
        wing, body = 8, 10
        color = (50, 50, 50)
        pygame.draw.circle(surface, color, (x, y), body//2)
        pygame.draw.polygon(surface, (220, 160, 40), [(x+6, y), (x+12, y-2), (x+12, y+2)])
        wy = int(y + math.sin(b['flap']*2.0) * 6)
        pygame.draw.line(surface, color, (x-2, y), (x-2-wing, wy), 3)
        pygame.draw.line(surface, color, (x+2, y), (x+2+wing, wy), 3)

def draw_castle_and_flag(surface, cam_x):
    cx = end_scene['castle_x'] - cam_x
    ground_y = SCREEN_HEIGHT - TILE_SIZE
    pygame.draw.rect(surface, (170, 100, 70), (cx, ground_y - 120, 150, 120))
    pygame.draw.rect(surface, (120, 70, 50), (cx, ground_y - 120, 150, 120), 3)
    for i in range(5):
        pygame.draw.rect(surface, (170, 100, 70), (cx + 10 + i*28, ground_y - 140, 18, 20))
    pygame.draw.rect(surface, (60, 40, 30), (cx + 60, ground_y - 50, 30, 50))
    pole_x = cx + 160
    pygame.draw.rect(surface, (220, 220, 220), (pole_x, end_scene['pole_top_y'], 6, end_scene['pole_base_y'] - end_scene['pole_top_y']))
    flag_w, flag_h = 60, 36
    fy = end_scene['flag_y']
    pygame.draw.rect(surface, (230, 30, 30), (pole_x + 6, fy, flag_w, flag_h))
    pygame.draw.rect(surface, (255, 255, 255), (pole_x + 6, fy, flag_w, flag_h), 2)
    small = pygame.font.Font(None, 28)
    surface.blit(small.render("vipul", True, (255, 255, 255)), (pole_x + 10, fy + flag_h//2 - small.get_height()//2))
    return pole_x, flag_w, flag_h

def process_end_scene(dt):
    if not level_completed:
        return
    ph = end_scene['phase']
    if ph == 'approach':
        if player.rect.x < end_scene['target_x']:
            player.rect.x += int(120 * dt)
            player.facing_right = True
        else:
            end_scene['phase'] = 'wave'
            end_scene['wave_timer'] = 1.2
            end_scene['wave_phase'] = 0.0
    elif ph == 'wave':
        end_scene['wave_timer'] -= dt
        end_scene['wave_phase'] += dt * 12.0
        if end_scene['wave_timer'] <= 0:
            end_scene['phase'] = 'raise'
            end_scene['raising'] = True
    elif ph == 'raise' and end_scene['raising']:
        end_scene['flag_y'] = max(end_scene['pole_top_y'] + 10, end_scene['flag_y'] - int(80 * dt))
        if end_scene['flag_y'] <= end_scene['pole_top_y'] + 10:
            end_scene['raising'] = False
            end_scene['phase'] = 'done'

current_level = 1
level_file = os.path.join(DATA_DIR, f'level{current_level}.csv')
highscore_file = os.path.join(DATA_DIR, 'highscore.json')
ai_state_file = os.path.join(DATA_DIR, 'ai_state.json')

# high-level states
menu_state = 'start'
game_running = False
show_autoplayer = False
autotest_enabled = False
autotest_deadline_ms = 0

# create adaptive AI (guard against bad json)
try:
    adaptive_ai = AdaptiveAI(ai_state_file)
except Exception:
    print("[warn] AdaptiveAI construction failed, creating default AI state.")
    try:
        adaptive_ai = AdaptiveAI(None)
    except Exception:
        adaptive_ai = None

ai_save_timer = 0.0

# logging helper
def _log(msg):
    print(msg)
    try:
        sys.stdout.flush()
    except Exception:
        pass

# game globals (initialized in reset_game)
player = None
level = None
bullets = []
enemies = []
coins = []
score = 0
lives = 3
game_camera = {'x': 0}
hud = None
clouds = []
birds = []
level_completed = False
level_complete_timer = 0.0
movers = []
spikes = []
end_scene = {
    'castle_x': 0,
    'pole_base_y': 0,
    'pole_top_y': 0,
    'flag_y': 0,
    'raising': False,
    'phase': 'idle',
    'target_x': 0,
    'wave_phase': 0.0,
    'wave_timer': 0.0,
}

def advance_level(loop_to_1=True):
    global current_level, level_file
    next_level = current_level + 1
    candidate = os.path.join(DATA_DIR, f'level{next_level}.csv')
    if os.path.exists(candidate):
        current_level = next_level
        level_file = candidate
    else:
        if loop_to_1:
            current_level = 1
            level_file = os.path.join(DATA_DIR, 'level1.csv')
        else:
            # fallback keeps current level
            level_file = os.path.join(DATA_DIR, f'level{current_level}.csv')

def reset_game():
    global player, level, bullets, enemies, score, lives, game_camera, hud, coins, level_file, clouds, birds, level_completed, level_complete_timer, movers, spikes, end_scene

    # start background music for the level (replace existing music if any)
    try:
        if pygame.mixer.get_init():
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
            pygame.mixer.music.load(os.path.join(SOUND_DIR, 'music.mp3'))
            pygame.mixer.music.play(-1)
            apply_volume()
    except Exception:
        print("[warn] music not loaded")

    _log('[reset] start')

    # ✅ ensure valid level_file before using it
    if not os.path.exists(level_file):
        alt_file = os.path.join("levels", "level1.txt")
        if os.path.exists(alt_file):
            level_file = alt_file
        else:
            raise FileNotFoundError(f"Level file missing: {level_file}")

    # load level safely
    level = Level(level_file)

    # Fallback: synthesize a ground if no platforms
    if not getattr(level, 'platforms', []):
        tiles = max(30, SCREEN_WIDTH // TILE_SIZE)
        y = SCREEN_HEIGHT - TILE_SIZE
        level.platforms = [pygame.Rect(x * TILE_SIZE, y, TILE_SIZE, TILE_SIZE) for x in range(tiles)]
        level.width = tiles
        level.height = max(1, getattr(level, 'height', 0))

    # create player
    player = Player(level.player_spawn, SCREEN_HEIGHT)
    bullets = []
    enemies = []
    coins = []
    score = 0
    lives = 3
    game_camera = {'x': 0}
    hud = HUD(SCREEN_WIDTH)
    level_completed = False
    level_complete_timer = 0.0

    # Decorative background actors
    clouds = []
    for _ in range(8):
        scale = random.uniform(0.6, 1.4)
        y = random.randint(20, SCREEN_HEIGHT // 2)
        speed = random.uniform(10, 30) * (0.6 + (1.6 - scale))  # smaller clouds move slightly faster
        x = random.randint(0, SCREEN_WIDTH)
        clouds.append({'x': x, 'y': y, 'scale': scale, 'speed': speed})

    birds = []
    for _ in range(4):
        y = random.randint(80, SCREEN_HEIGHT // 2 + 80)
        speed = random.uniform(60, 120)
        x = random.randint(0, SCREEN_WIDTH)
        flap = random.uniform(0, 6.28)
        birds.append({'x': x, 'y': y, 'speed': speed, 'flap': flap})

    # Disable movers/spikes for stability
    movers = []
    spikes = []

    # Configure end-of-level castle/flag position near far right of the level
    castle_margin = 220
    end_scene['castle_x'] = max(60, level.width * TILE_SIZE - castle_margin)
    ground_y = SCREEN_HEIGHT - TILE_SIZE
    pole_h = 160
    end_scene['pole_base_y'] = ground_y
    end_scene['pole_top_y'] = ground_y - pole_h
    end_scene['flag_y'] = end_scene['pole_base_y'] - 40
    end_scene['raising'] = False
    end_scene['phase'] = 'idle'
    end_scene['target_x'] = 0
    end_scene['wave_phase'] = 0.0
    end_scene['wave_timer'] = 0.0

    # enemies (support both typed (etype, pos) and legacy (x,y) formats)
    for spawn in getattr(level, 'enemy_spawns', []):
        try:
            if isinstance(spawn, tuple) and len(spawn) == 2 and isinstance(spawn[0], str):
                etype, pos = spawn
            else:
                etype, pos = 'P', spawn
            speed_scale = 1.0 + 0.15 * (current_level - 1)
            # Force all enemies to be Patrollers (no chasing)
            params = (adaptive_ai.get_params() if adaptive_ai else {}).copy()
            params['speed'] = int(60 * speed_scale)
            enemies.append(Patroller(pos, params))
        except Exception:
            _log(f"[warn] failed to spawn enemy {spawn}")

    # Extra enemies to make it livelier: sample platforms to place patrollers (scaled by difficulty)
    try:
        plats = [p[0] if isinstance(p, tuple) else p for p in getattr(level, 'platforms', [])]
        plats = [r for r in plats if isinstance(r, pygame.Rect)]
        random.shuffle(plats)
        extra = min(12, max(4, len(plats)//15 + (current_level - 1)))
        for i in range(extra):
            rect = plats[i % len(plats)]
            x = rect.x + 8
            y = rect.top - 44
            speed_scale = 1.0 + 0.15 * (current_level - 1)
            params = (adaptive_ai.get_params() if adaptive_ai else {}).copy()
            params['speed'] = int(60 * speed_scale)
            enemies.append(Patroller((x, y), params))
    except Exception:
        _log('[warn] failed to add extra enemies')

    # coins (safe fallback)
    for pos in getattr(level, 'coin_spawns', []):
        coins.append({'pos': pos, 'rect': pygame.Rect(pos[0], pos[1], TILE_SIZE, TILE_SIZE), 'taken': False})

    # ✅ use len(getattr(...)) so it won’t crash if missing
    _log(f"[reset] done platforms={len(getattr(level, 'platforms', []))} "
         f"enemies={len(getattr(level, 'enemy_spawns', []))} "
         f"coins={len(getattr(level, 'coin_spawns', []))} "
         f"spawn={getattr(level, 'player_spawn', (0,0))}")

def save_score(new_score):
    highscore = load_highscore(highscore_file)
    if new_score > highscore:
        save_highscore(highscore_file, new_score)

def handle_menu():
    global menu_state, game_running
    title_font = pygame.font.Font(None, 56)
    font = pygame.font.Font(None, 40)
    title_surf = title_font.render("AI Mario – Smart Platform Adventure", True, WHITE)
    hint_font = pygame.font.Font(None, 20)

    btn_w, btn_h = 260, 64
    start_rect = pygame.Rect((SCREEN_WIDTH - btn_w) // 2, 220, btn_w, btn_h)
    quit_rect = pygame.Rect((SCREEN_WIDTH - btn_w) // 2, 300, btn_w, btn_h)

    _log('[menu] entering')
    # Ensure menu_state is 'start' when entering
    menu_state = 'start'
    while menu_state == 'start':
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    game_running = True
                    menu_state = 'game'
                    _log('[menu] start via key')
                    return
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if start_rect.collidepoint(mouse_pos):
                    game_running = True
                    menu_state = 'game'
                    _log('[menu] start via click')
                    return
                elif quit_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        mouse_pos = pygame.mouse.get_pos()

        # draw
        screen.fill(SKY)
        screen.blit(title_surf, ((SCREEN_WIDTH - title_surf.get_width()) // 2, 100))

        # Start button
        start_hover = start_rect.collidepoint(mouse_pos)
        start_color = (70, 130, 180) if start_hover else (50, 100, 150)
        pygame.draw.rect(screen, start_color, start_rect, border_radius=8)
        start_surf = font.render("Start", True, WHITE)
        screen.blit(start_surf, (start_rect.centerx - start_surf.get_width() // 2,
                                 start_rect.centery - start_surf.get_height() // 2))

        # Quit button
        quit_hover = quit_rect.collidepoint(mouse_pos)
        quit_color = (200, 70, 70) if quit_hover else (160, 50, 50)
        pygame.draw.rect(screen, quit_color, quit_rect, border_radius=8)
        quit_surf = font.render("Quit", True, WHITE)
        screen.blit(quit_surf, (quit_rect.centerx - quit_surf.get_width() // 2,
                                quit_rect.centery - quit_surf.get_height() // 2))

        hint = hint_font.render("Press Enter/Space or click a button", True, WHITE)
        screen.blit(hint, ((SCREEN_WIDTH - hint.get_width()) // 2, quit_rect.bottom + 12))

        pygame.display.flip()
        clock.tick(FPS)

def draw_camera_bg():
    top = (140, 200, 255)
    bottom = (90, 150, 210)
    steps = SCREEN_HEIGHT
    for y in range(steps):
        t = y / max(1, steps - 1)
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

def update_camera():
    cam_x = clamp(player.rect.centerx - SCREEN_WIDTH // 2, 0, level.width * TILE_SIZE - SCREEN_WIDTH)
    game_camera['x'] = cam_x

def game_loop():
    global score, lives, game_running, show_autoplayer, ai_save_timer, level_completed, level_complete_timer
    run_auto = False
    paused = False
    _log('[game] enter')

    try:
        # ensure required game globals exist
        if player is None or level is None:
            raise RuntimeError("Game not initialized: player or level missing")

        while game_running:
            dt = clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_running = False
                        return
                    if event.key == pygame.K_F1:
                        show_autoplayer = not show_autoplayer
                    if event.key == pygame.K_p:
                        paused = not paused
                    if event.key == pygame.K_m:
                        toggle_mute()
                    if event.key == pygame.K_r:
                        # restart current level
                        try:
                            reset_game()
                        except Exception:
                            _log('[error] reset_game failed on restart:')
                            traceback.print_exc()
                            game_running = False
                            return
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if get_sound_button_rect().collidepoint(event.pos):
                        toggle_mute()

            keys = pygame.key.get_pressed()

            if paused:
                # Draw paused overlay and continue loop without updating game state
                if BACKGROUND_IMG:
                    screen.blit(BACKGROUND_IMG, (0, 0))
                else:
                    draw_camera_bg()
                level.draw(screen, game_camera['x'])

            # Draw end-of-level castle and flag (after level, before entities)
            cx = end_scene['castle_x'] - game_camera['x']
            ground_y = SCREEN_HEIGHT - TILE_SIZE
            # castle body
            pygame.draw.rect(screen, (170, 100, 70), (cx, ground_y - 120, 150, 120))
            pygame.draw.rect(screen, (120, 70, 50), (cx, ground_y - 120, 150, 120), 3)
            # battlements
            for i in range(5):
                pygame.draw.rect(screen, (170, 100, 70), (cx + 10 + i*28, ground_y - 140, 18, 20))
            # door
            pygame.draw.rect(screen, (60, 40, 30), (cx + 60, ground_y - 50, 30, 50))
            # flag pole
            pole_x = cx + 160
            pygame.draw.rect(screen, (220, 220, 220), (pole_x, end_scene['pole_top_y'], 6, end_scene['pole_base_y'] - end_scene['pole_top_y']))
            # flag
            flag_w, flag_h = 60, 36
            fy = end_scene['flag_y']
            pygame.draw.rect(screen, (230, 30, 30), (pole_x + 6, fy, flag_w, flag_h))
            pygame.draw.rect(screen, (255, 255, 255), (pole_x + 6, fy, flag_w, flag_h), 2)
            small = pygame.font.Font(None, 28)
            txt = small.render("vipul", True, (255, 255, 255))
            screen.blit(txt, (pole_x + 10, fy + flag_h//2 - txt.get_height()//2))

            # Draw player waving arm when in wave phase (simple overlay arm)
            if level_completed and end_scene['phase'] in ('wave', 'raise'):
                px = player.rect.x - game_camera['x']
                py = player.rect.y
                # arm swing
                ang = math.sin(end_scene['wave_phase'])
                arm_len = 18
                x1 = px + (26 if player.facing_right else 6)
                y1 = py + 16
                x2 = int(x1 + arm_len * math.cos(1.2 + ang*0.8) * (1 if player.facing_right else -1))
                y2 = int(y1 - arm_len * math.sin(1.2 + ang*0.8))
                pygame.draw.line(screen, (255, 220, 200), (x1, y1), (x2, y2), 4)

            
            # Level complete overlay (with congratulations) after raise completes or timer ends
            if level_completed and (end_scene['phase'] == 'done' or level_complete_timer <= 0):
                level_complete_timer -= dt
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 140))
                screen.blit(overlay, (0, 0))
                title = pygame.font.Font(None, 72).render("Congratulations!", True, (255, 255, 255))
                sub = pygame.font.Font(None, 40).render("You completed the level", True, (255, 255, 0))
                screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 80))
                screen.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, SCREEN_HEIGHT//2 - 20))
                if level_complete_timer <= 0:
                    # Progress after showing overlay
                    advance_level(loop_to_1=True)
                    try:
                        reset_game()
                    except Exception:
                        _log('[error] reset_game failed after level completion:')
                        traceback.print_exc()
                        game_running = False
                        return
                pygame.display.flip()
                continue

            if show_autoplayer and not level_completed:
                run_auto = True
            else:
                run_auto = False

            if run_auto and adaptive_ai and not level_completed:
                AutoPlayer.control(player, level, enemies, coins, bullets, sound_jump, sound_shoot)
            else:
                move_left = keys[pygame.K_a] or keys[pygame.K_LEFT]
                move_right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
                jump = keys[pygame.K_w] or keys[pygame.K_SPACE]
                shoot = keys[pygame.K_j] or keys[pygame.K_k]
                if not level_completed:
                    player.handle_input(move_left, move_right, jump, shoot, bullets, sound_jump, sound_shoot)

            # Use only static level platforms for collisions
            if not level_completed:
                player.update(level.platforms, dt)
                update_camera()

            # Update decorative actors (parallax, independent of camera)
            for c in clouds:
                c['x'] -= c['speed'] * dt
                if c['x'] < -220:
                    c['x'] = SCREEN_WIDTH + random.randint(10, 200)
                    c['y'] = random.randint(20, SCREEN_HEIGHT // 2)
                    c['scale'] = random.uniform(0.6, 1.4)
                    c['speed'] = random.uniform(10, 30) * (0.6 + (1.6 - c['scale']))

            for b in birds:
                b['x'] -= b['speed'] * dt
                b['flap'] += dt * 8.0
                if b['x'] < -60:
                    b['x'] = SCREEN_WIDTH + random.randint(50, 300)
                    b['y'] = random.randint(80, SCREEN_HEIGHT // 2 + 80)
                    b['speed'] = random.uniform(60, 120)
                    b['flap'] = random.uniform(0, 6.28)

            # End-scene phases: approach -> wave -> raise -> overlay
            if level_completed:
                if end_scene['phase'] == 'approach':
                    # Move player toward the pole
                    if player.rect.x < end_scene['target_x']:
                        player.rect.x += int(120 * dt)
                        player.facing_right = True
                    else:
                        end_scene['phase'] = 'wave'
                        end_scene['wave_timer'] = 1.2
                        end_scene['wave_phase'] = 0.0
                elif end_scene['phase'] == 'wave':
                    end_scene['wave_timer'] -= dt
                    end_scene['wave_phase'] += dt * 12.0
                    if end_scene['wave_timer'] <= 0:
                        end_scene['phase'] = 'raise'
                        end_scene['raising'] = True
                elif end_scene['phase'] == 'raise':
                    if end_scene['raising']:
                        end_scene['flag_y'] = max(end_scene['pole_top_y'] + 10, end_scene['flag_y'] - int(80 * dt))
                        if end_scene['flag_y'] <= end_scene['pole_top_y'] + 10:
                            end_scene['raising'] = False
                            end_scene['phase'] = 'done'

            # bullets
            for bullet in bullets[:]:
                bullet.update(dt)
                for enemy in enemies:
                    if bullet.rect.colliderect(enemy.rect):
                        enemy.health -= 1
                        try:
                            enemy.hit_timer = 0.12
                        except Exception:
                            pass
                        if bullet in bullets:
                            bullets.remove(bullet)
                        if enemy.health <= 0:
                            score += 100
                            if enemy in enemies:
                                enemies.remove(enemy)
                            break
                if bullet.lifetime <= 0 and bullet in bullets:
                    bullets.remove(bullet)

            # enemies
            for enemy in enemies[:]:
                if not level_completed:
                    enemy.update(level.platforms, player, dt, game_camera['x'])
                if enemy.rect.colliderect(player.rect) and getattr(player, 'invuln_timer', 0) <= 0:
                    lives -= 1
                    player.invuln_timer = 1.2
                    if sound_coin:
                        sound_coin.play()
                    if lives == 0:
                        save_score(score)
                        game_running = False
                        return
                    else:
                        player.respawn(level.player_spawn)
                if enemy.rect.top > SCREEN_HEIGHT:
                    if enemy in enemies:
                        enemies.remove(enemy)

            # coins
            for coin in coins:
                if not coin['taken'] and player.rect.colliderect(coin['rect']):
                    coin['taken'] = True
                    score += 10
                    if sound_coin:
                        sound_coin.play()

            # AI bookkeeping
            try:
                if adaptive_ai:
                    adaptive_ai.track_score(score)
                    adaptive_ai.update_enemies(enemies)
            except Exception:
                _log("[warn] adaptive_ai threw during update; continuing")
            ai_save_timer += dt
            if ai_save_timer >= 2.0:
                try:
                    if adaptive_ai:
                        adaptive_ai.save()
                except Exception:
                    _log("[warn] adaptive_ai.save failed")
                ai_save_timer = 0.0

            # Trigger end scene (castle + flag) slightly before absolute level end
            end_trigger_x = end_scene['castle_x'] - 20
            if not level_completed and player.rect.right >= end_trigger_x:
                save_score(score)
                level_completed = True
                # Approach pole before raising
                level_complete_timer = 4.0
                end_scene['phase'] = 'approach'
                end_scene['target_x'] = end_scene['castle_x'] + 160 - 18  # stand by the pole
                end_scene['raising'] = False

            # Spike hazards disabled

            # fall death
            if player.rect.top > SCREEN_HEIGHT + 120:
                if getattr(player, 'invuln_timer', 0) <= 0:
                    lives -= 1
                    player.invuln_timer = 1.2
                    if lives == 0:
                        save_score(score)
                        game_running = False
                        return
                    else:
                        player.respawn(level.player_spawn)

            # drawing
            if BACKGROUND_IMG:
                screen.blit(BACKGROUND_IMG, (0, 0))
            else:
                draw_camera_bg()

            # Draw clouds (behind level)
            for c in clouds:
                sx = int(60 * c['scale'])
                sy = int(30 * c['scale'])
                x = int(c['x'])
                y = int(c['y'])
                # simple puffy cloud using ellipses
                pygame.draw.ellipse(screen, (255, 255, 255), (x, y, sx, sy))
                pygame.draw.ellipse(screen, (255, 255, 255), (x + sx//3, y - sy//3, sx, sy))
                pygame.draw.ellipse(screen, (255, 255, 255), (x + sx//2, y, sx, sy))

            level.draw(screen, game_camera['x'])

            # Draw birds (mid-ground, between level and player)
            for b in birds:
                x = int(b['x'])
                y = int(b['y'] + math.sin(b['flap']) * 6)
                wing = 8
                body = 10
                color = (50, 50, 50)
                # body
                pygame.draw.circle(screen, color, (x, y), body//2)
                # beak
                pygame.draw.polygon(screen, (220, 160, 40), [(x+6, y), (x+12, y-2), (x+12, y+2)])
                # wings (flapping)
                wy = int(y + math.sin(b['flap']*2.0) * 6)
                pygame.draw.line(screen, color, (x-2, y), (x-2-wing, wy), 3)
                pygame.draw.line(screen, color, (x+2, y), (x+2+wing, wy), 3)
            for coin in coins:
                if not coin['taken']:
                    cx = coin['rect'].x - game_camera['x'] + coin['rect'].width // 2
                    cy = coin['rect'].y + coin['rect'].height // 2
                    pygame.draw.circle(screen, (255, 215, 0), (cx, cy), coin['rect'].width // 2)
            player.draw(screen, game_camera['x'])
            for enemy in enemies:
                enemy.draw(screen, game_camera['x'])
            for bullet in bullets:
                bullet.draw(screen, game_camera['x'])
            hud.draw(screen, score, lives, current_level, show_autoplayer)
            # Draw mute button last so it stays on top
            draw_sound_button(screen)
            pygame.display.flip()

    except Exception:
        _log('[error] exception inside game_loop:')
        traceback.print_exc()
        # pause so you can read the error in terminal
        pygame.time.wait(1500)
        # ensure we return to menu in a safe state
        game_running = False
        menu_state = 'start'

if __name__ == "__main__":
    # make errors visible in console
    sys.tracebacklimit = None

    # Parse simple CLI flag for automated soak testing
    for arg in sys.argv[1:]:
        if arg.startswith('--autotest='):
            try:
                seconds = float(arg.split('=', 1)[1])
            except Exception:
                seconds = 120.0
            autotest_enabled = True
            autotest_deadline_ms = pygame.time.get_ticks() + int(seconds * 1000)

    if autotest_enabled:
        # Bypass menu and run continuous games with AutoPlayer until deadline
        show_autoplayer = True
        while pygame.time.get_ticks() < autotest_deadline_ms:
            try:
                reset_game()
            except Exception:
                _log('[error] reset_game failed during autotest:')
                traceback.print_exc()
                break
            _log('[main] game_loop (autotest)')
            game_running = True
            game_loop()
        _log('[autotest] completed')
        pygame.quit()
        sys.exit(0)

    while True:
        try:
            # Reset states each cycle to avoid stale values
            menu_state = 'start'
            game_running = False
            _log('[main] handle_menu')
            handle_menu()

            # user requested start -> initialize/reset game objects
            _log('[main] reset_game')
            try:
                reset_game()
            except Exception:
                _log('[error] reset_game failed:')
                traceback.print_exc()
                pygame.time.wait(2000)
                # return to menu rather than crashing
                menu_state = 'start'
                game_running = False
                continue

            _log('[main] game_loop')
            game_loop()

        except SystemExit:
            raise
        except Exception:
            _log('[error] exception in main loop:')
            traceback.print_exc()
            pygame.time.wait(1500)
            menu_state = 'start'
            game_running = False
