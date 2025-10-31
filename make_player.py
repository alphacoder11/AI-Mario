import cairosvg
import os

# Ensure the output folder exists
os.makedirs(os.path.join("assets", "tiles"), exist_ok=True)

# Convert player.svg → player.png
cairosvg.svg2png(url="player.svg", write_to=os.path.join("assets", "tiles", "player.png"))

print("✅ Player image created successfully at assets/tiles/player.png")
