# File: README.md

## AI Mario – Smart Platform Adventure

A side-scrolling 2D platformer in Python/Pygame featuring adaptive AI, tile-based maps, scoring, and AutoPlayer.

### Controls

- **Move left/right:** A/D or ←/→
- **Jump:** W or Space (hold for higher jump)
- **Shoot:** J or K
- **Menu:** Space/Enter (Start), Esc (Quit)
- **AutoPlayer toggle:** F1 (HUD shows ON/OFF status)

### How to Run (Windows / Linux / Mac)

1. Open terminal in project root.
2. Create a virtual environment
    - Windows: `python -m venv venv && venv\Scripts\activate`
    - Linux/macOS: `python3 -m venv venv && source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the game: `python main.py`
5. Run unit tests: `python -m unittest discover tests`

### Assets

- See `assets/README.md` for free asset links. The game runs with rectangles/circles by default, no downloads needed.
- To add sounds: put WAV files (`coin.wav`, `jump.wav`, `shoot.wav`) in `assets/sounds/`.

### Saving

- Highscore is saved automatically in `data/highscore.json`.
- AI state (enemy difficulty) is saved in `data/ai_state.json`.

### Viva/Presentation Notes

- AI explained in `REPORT.md`.
- Module and function explanations in `EXPLANATION.txt`.
