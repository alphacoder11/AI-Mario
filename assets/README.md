# File: assets/README.md

## Asset Usage Guidance

This project runs "out of the box" using procedural shapes for all graphics (rects/circles).
You do **not** need external images, but can enhance visuals with sprites/sounds.

**Where to get free sprites:**
- [Kenney.nl 2D Platformer Pack](https://kenney.nl/assets/platformer-pack)
- [OpenGameArt.org](https://opengameart.org)
- [itch.io free pixel packs](https://itch.io/game-assets/free/tag-pixel-art)

**How to add:**
- Place PNG images in `assets/` and update `player.draw()` / `enemy.draw()` etc. to use `pygame.image.load`.
- Place your sound files (WAV) in `assets/sounds/`. See code in `main.py` for optional fallback.

**Sound effects (optional):**
- Add your own `coin.wav`, `jump.wav`, `shoot.wav` in `assets/sounds`. If not present, procedural sounds are skipped gracefully.
- Free sounds: [freesound.org](https://www.freesound.org/), [OpenGameArt.org](https://opengameart.org/sounds)

**Testing assets**
- To test with just rectangles & circles: no change needed.

**Licensing**
- All assets must be CC0/public domain or licensed for classroom/demo use.
