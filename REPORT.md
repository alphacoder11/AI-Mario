# File: REPORT.md

## Project Summary

"AI Mario – Smart Platform Adventure" demonstrates procedural platform design, basic physics, adaptive AI, and modular code architecture in Python/Pygame for educational/academic use.

### AI Approaches Used

- **Patroller**: Moves horizontally, reverses at platform edges. Implements state switching ('patrol', 'turn'), checks for platform surface below.
- **Chaser**: Detects player using `detection_range`, switches between `idle` and `chase` states. Pursues via simple heuristics (distance check).
- **Adaptive AI**: Tracks average score, adjusts enemy speed and detection range after high scores/time. Difficulty parameters persist via JSON.
- **AutoPlayer**: Rule-based bot; moves right, jumps if no ground, shoots if danger, prioritizes nearest coin.

### Modular Structure

Classes organized by domain (`player.py`, `enemy.py`, etc.), functions explained in `EXPLANATION.txt`.

### Extensions

- Multi-level support; extend with more maps in `data/`.
- Enhance AutoPlayer with decision-tree for advanced moves.
- Integrate external sprites/sounds for improved aesthetics.
- Implement more enemy behaviors (e.g., jumpers, shooters).
- Support power-ups (extra life, invincibility).

### Sample Viva Questions

1. *How does the adaptive AI function and why is it useful?*
   - The AI increases enemy speed/detection_range based on player score/time, making gameplay more challenging for skilled players.

2. *Explain patrol and chase behaviors for enemies.*
   - Patrol: enemies move and turn at edges. Chasers use distance checks to chase players when within range.

3. *Describe the tile map loader parsing process.*
   - CSV files are parsed row-by-row; specific characters denote platforms, enemies, coins, and spawn points, creating platform and entity positions procedurally.

4. *How is collision handled in the game?*
   - All entities use `pygame.Rect` collision methods for bullet-enemy, player-platform, and player-coin interactions.

5. *How does the AutoPlayer work?*
   - AutoPlayer is a rule-based bot that analyzes ground ahead, jumps gaps, moves toward the goal/coins, and triggers shooting if danger is detected.
