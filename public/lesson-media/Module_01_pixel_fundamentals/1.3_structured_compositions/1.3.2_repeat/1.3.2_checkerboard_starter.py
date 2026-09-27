import numpy as np
from PIL import Image

# TODO 1: Define parameters
# What: set grid dimensions for an 8x8 board with 64px tiles
# Why: the tile size must divide evenly into 512 for seamless coverage
N_TILES = 8
TILE_SIZE = 64
SIZE = N_TILES * TILE_SIZE

# Define colors
BLACK = np.array([0, 0, 0], dtype=np.uint8)
GREEN = np.array([83, 168, 139], dtype=np.uint8)

# Create canvas
canvas = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)

# TODO 2: Write nested loops to iterate over the grid
# What: loop through every (x, y) position in the 8x8 grid
# Why: nested loops let you visit each tile systematically

    # TODO 3: Determine color using alternation logic
    # What: use (x + y) % 2 to pick BLACK or GREEN
    # Why: adjacent tiles always have opposite parity (even/odd sum)

    # TODO 4: Calculate slice positions (no spacing)
    # What: compute row_start, row_stop, col_start, col_stop
    # Why: when spacing=0, the formula simplifies to i * tile_size

    # TODO 5: Place the tile on the canvas
    # What: assign the colour to the computed slice region
    # Why: NumPy broadcasting fills the entire tile with one assignment

# Save result
result = Image.fromarray(canvas, mode='RGB')
result.save('my_checkerboard.png')
