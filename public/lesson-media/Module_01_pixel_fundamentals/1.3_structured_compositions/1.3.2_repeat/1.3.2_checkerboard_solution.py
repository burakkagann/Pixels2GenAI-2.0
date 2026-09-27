import numpy as np
from PIL import Image

N_TILES = 8
TILE_SIZE = 64
SIZE = N_TILES * TILE_SIZE

BLACK = np.array([0, 0, 0], dtype=np.uint8)
GREEN = np.array([83, 168, 139], dtype=np.uint8)

canvas = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)

for y in range(N_TILES):
    for x in range(N_TILES):
        # Alternation logic using modulo
        if (x + y) % 2 == 0:
            color = BLACK
        else:
            color = GREEN

        # Position calculation (no spacing)
        row_start = y * TILE_SIZE
        row_stop = (y + 1) * TILE_SIZE
        col_start = x * TILE_SIZE
        col_stop = (x + 1) * TILE_SIZE

        # Place tile
        canvas[row_start:row_stop, col_start:col_stop] = color

result = Image.fromarray(canvas, mode='RGB')
result.save('checkerboard.png')
