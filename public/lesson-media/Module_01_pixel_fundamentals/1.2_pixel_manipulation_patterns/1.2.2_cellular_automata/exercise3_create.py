import numpy as np
from PIL import Image
from scipy.ndimage import convolve

# Helper functions (provided, do not edit)

def grid_to_image(grid, scale=8):
    """Convert binary grid to RGB image."""
    gray = np.repeat(np.repeat(grid * 255, scale, axis=0), scale, axis=1)
    return np.stack([gray, gray, gray], axis=2).astype(np.uint8)

def game_of_life_step(grid):
    """Apply one generation of Conway's Game of Life rules."""
    kernel = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
    neighbor_count = convolve(grid, kernel, mode='wrap')
    return ((neighbor_count == 3) | ((grid == 1) & (neighbor_count == 2))).astype(int)

# Initialize a 40x40 grid (all cells start dead)
grid = np.zeros((40, 40), dtype=int)

# TODO 1: Place a beacon oscillator at position (5, 5).
#         A beacon is two 2x2 blocks offset diagonally:
#           ■ ■ . .
#           ■ . . .       (compact form)
#           . . . ■
#           . . ■ ■
#         The top-left block is done for you. Complete the bottom-right.
grid[5:7, 5:7] = [[1, 1], [1, 0]]    # Top-left block
grid[7:9, 7:9] = ...                  # Bottom-right block

# TODO 2: Place a glider spaceship at position (20, 10).
#         The glider pattern is a 3x3 shape:
#           . ■ .
#           . . ■
#           ■ ■ ■
#         Assign this as a 2D list to grid[20:23, 10:13].
grid[20:23, 10:13] = ...

# TODO 3: Run the evolution loop for 20 generations.
#         Each iteration: advance the grid one step, then
#         print the generation number and living cell count.
for generation in range(20):
    ...

# Save the final result
Image.fromarray(grid_to_image(grid)).save('exercise3_result.png')
print("Pattern garden saved!")

# ---------------------------------------------------------
# MAKE IT YOUR OWN (after completing the TODOs above):
#
#   - Add a blinker: grid[row, col:col+3] = [1, 1, 1]
#   - Add a block (still life): grid[row:row+2, col:col+2] = 1
#   - Try placing two gliders on a collision course!
#   - Increase the grid to 60x60 and add more patterns
# ---------------------------------------------------------
