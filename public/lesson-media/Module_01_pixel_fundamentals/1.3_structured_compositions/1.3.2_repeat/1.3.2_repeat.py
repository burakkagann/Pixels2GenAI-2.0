import numpy as np
from PIL import Image

# Configuration parameters
N_TILES = 4          # Number of tiles per row/column
TILE_WIDTH = 125     # Width of each tile in pixels
SPACING = 15         # Gap between tiles
SIZE = TILE_WIDTH * N_TILES + SPACING

# Create blank canvas
canvas = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)

# Nested loops to place tiles
for y in range(N_TILES):
    for x in range(N_TILES):
        # Calculate color based on position
        color = (50 * y + 50, 50 * x + 50, 0)

        # Calculate slice positions algorithmically
        row_start = SPACING + y * TILE_WIDTH
        row_stop = (y + 1) * TILE_WIDTH
        col_start = SPACING + x * TILE_WIDTH
        col_stop = (x + 1) * TILE_WIDTH

        # Place tile
        canvas[row_start:row_stop, col_start:col_stop] = color

# Save result
result = Image.fromarray(canvas, mode='RGB')
result.save('repeat.png')
