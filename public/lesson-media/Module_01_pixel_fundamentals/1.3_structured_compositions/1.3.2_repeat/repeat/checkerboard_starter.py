
import numpy as np
from PIL import Image

# TODO: Define parameters
# Hint: N_TILES = 8 for a standard checkerboard
# Hint: TILE_SIZE should divide evenly into 512 (512 / 8 = 64)
# Hint: SIZE = N_TILES * TILE_SIZE (no spacing needed)

N_TILES = 0  # TODO: Set to 8
TILE_SIZE = 0  # TODO: Calculate based on desired canvas size (512 pixels)
SIZE = 0  # TODO: Calculate total canvas size

# TODO: Define colors
# Hint: BLACK = [0, 0, 0], GREEN = [83, 168, 139] (inspired by Tanjiro's haori from Demon Slayer)
BLACK = None  # TODO: Set black color
GREEN = None  # TODO: Set green color

# TODO: Create canvas
# Hint: Use np.zeros((SIZE, SIZE, 3), dtype=np.uint8)
canvas = None  # TODO: Create blank canvas

# TODO: Nested loops to place tiles
# Hint: for y in range(N_TILES):
#           for x in range(N_TILES):

    # TODO: Determine color using alternation logic
    # Hint: if (x + y) % 2 == 0, use BLACK, else use GREEN

    # TODO: Calculate slice positions
    # Hint: When spacing = 0, formula simplifies to:
    #       row_start = y * TILE_SIZE
    #       row_stop = (y + 1) * TILE_SIZE

    # TODO: Place tile using slicing
    # Hint: canvas[row_start:row_stop, col_start:col_stop] = color

# TODO: Save result
# Hint: result = Image.fromarray(canvas, mode='RGB')
#       result.save('my_checkerboard.png')
