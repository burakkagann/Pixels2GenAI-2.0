

import numpy as np
from PIL import Image

# Configuration parameters
N_TILES = 8              # 8x8 checkerboard (standard chess/checkers board)
TILE_SIZE = 64           # 64 pixels per square (creates 512x512 canvas)
SIZE = N_TILES * TILE_SIZE  # Total canvas size (512 pixels)

# Colors
BLACK = np.array([0, 0, 0], dtype=np.uint8)
GREEN = np.array([83, 168, 139], dtype=np.uint8)  # Inspired by Tanjiro's haori (Demon Slayer)

# Step 1: Create blank canvas
canvas = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)

print(f"Creating {N_TILES}x{N_TILES} checkerboard pattern...")
print(f"Canvas size: {SIZE}x{SIZE} pixels")
print(f"Tile size: {TILE_SIZE}x{TILE_SIZE} pixels\n")

# Step 2: Nested loops to place alternating tiles
for y in range(N_TILES):
    for x in range(N_TILES):

        # Step 3: Determine color using alternation logic
        # (x + y) % 2 gives us:
        #   - 0 when x+y is even (black squares)
        #   - 1 when x+y is odd (green squares)
        if (x + y) % 2 == 0:
            color = BLACK
        else:
            color = GREEN

        # Step 4: Calculate position (no spacing for seamless tiles)
        # Formula simplifies when spacing = 0:
        row_start = y * TILE_SIZE
        row_stop = (y + 1) * TILE_SIZE
        col_start = x * TILE_SIZE
        col_stop = (x + 1) * TILE_SIZE

        # Step 5: Place tile
        canvas[row_start:row_stop, col_start:col_stop] = color

# Step 6: Save result
result = Image.fromarray(canvas, mode='RGB')
result.save('checkerboard.png')

print(f"Created {N_TILES}x{N_TILES} checkerboard")
print(f"Total tiles: {N_TILES * N_TILES}")
print(f"Black tiles: {(N_TILES * N_TILES) // 2}")
print(f"Green tiles: {(N_TILES * N_TILES) // 2}")
print(f"Output saved as: checkerboard.png")

# Educational note
print("\nAlternation logic explained:")
print("When (x + y) is even: Black")
print("When (x + y) is odd: Green")
print("Examples:")
for y in range(2):
    for x in range(2):
        sum_val = x + y
        color_name = "Black" if sum_val % 2 == 0 else "Green"
        print(f"  Position ({x},{y}): x+y={sum_val}, {sum_val} % 2 = {sum_val % 2} -> {color_name}")
