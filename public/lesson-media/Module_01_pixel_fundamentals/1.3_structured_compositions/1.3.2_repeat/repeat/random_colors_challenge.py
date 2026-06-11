import numpy as np
from PIL import Image

# Configuration
N_TILES = 10         # Create a larger 10x10 grid
TILE_WIDTH = 50      # Smaller tiles to fit more on canvas
SPACING = 5          # Small spacing between tiles
SIZE = TILE_WIDTH * N_TILES + SPACING  # Total canvas size

# Seed for reproducibility (optional - comment out for different results each time)
np.random.seed(42)

# Create blank canvas
canvas = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)

print(f"Creating {N_TILES}x{N_TILES} random color grid...")
print(f"Canvas size: {SIZE}x{SIZE} pixels")
print(f"Total tiles: {N_TILES * N_TILES}\n")

# Nested loops to place randomly colored tiles
for y in range(N_TILES):
    for x in range(N_TILES):

        # Generate random color for each tile
        # np.random.randint() generates random integers in range [0, 256)
        red = np.random.randint(0, 256)
        green = np.random.randint(0, 256)
        blue = np.random.randint(0, 256)
        color = (red, green, blue)

        # Calculate position
        row_start = SPACING + y * TILE_WIDTH
        row_stop = (y + 1) * TILE_WIDTH
        col_start = SPACING + x * TILE_WIDTH
        col_stop = (x + 1) * TILE_WIDTH

        # Place tile
        canvas[row_start:row_stop, col_start:col_stop] = color

# Save result
result = Image.fromarray(canvas, mode='RGB')
result.save('repeat_challenge.png')

