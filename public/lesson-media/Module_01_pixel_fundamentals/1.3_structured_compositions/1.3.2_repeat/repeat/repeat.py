import numpy as np
from PIL import Image

# Configuration parameters
N_TILES = 4          # Number of tiles per row/column (creates 4×4 grid)
TILE_WIDTH = 125     # Width of each square tile in pixels
SPACING = 15         # Gap between tiles in pixels (creates visual separation)
SIZE = TILE_WIDTH * N_TILES + SPACING  # Total canvas size (515 pixels)

# Step 1: Create blank canvas
# Initialize a black image with 3 color channels (RGB)
canvas = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)

print(f"Creating {N_TILES}×{N_TILES} tiling pattern...")
print(f"Canvas size: {SIZE}×{SIZE} pixels")
print(f"Tile size: {TILE_WIDTH}×{TILE_WIDTH} pixels")
print(f"Spacing: {SPACING} pixels\n")

# Step 2: Use nested loops to place tiles
# Outer loop iterates through rows (y-position)
for y in range(N_TILES):
    # Inner loop iterates through columns (x-position)
    for x in range(N_TILES):

        # Step 3: Calculate color based on position (creates gradient effect)
        # Red increases as you move down (higher y values)
        # Green increases as you move right (higher x values)
        # Blue stays at 0
        color = (50 * y + 50, 50 * x + 50, 0)

        # Step 4: Calculate slice positions algorithmically
        # Formula: start = spacing + (loop_variable * tile_width)
        # This ensures even spacing and correct positioning
        row_start = SPACING + y * TILE_WIDTH      # Top edge of tile
        row_stop = (y + 1) * TILE_WIDTH           # Bottom edge of tile
        col_start = SPACING + x * TILE_WIDTH      # Left edge of tile
        col_stop = (x + 1) * TILE_WIDTH           # Right edge of tile

        # Step 5: Place colored tile using calculated positions
        # This uses the slicing syntax from Module 1.3.1, but with computed values
        canvas[row_start:row_stop, col_start:col_stop] = color

        # Diagnostic output to show loop execution
        print(f"Tile ({x},{y}): color={color}, position=[{row_start}:{row_stop}, {col_start}:{col_stop}]")

# Step 6: Save result
result = Image.fromarray(canvas, mode='RGB')
result.save('repeat.png')

