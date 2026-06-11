import numpy as np
from PIL import Image
from scipy.ndimage import convolve

# Step 1: Define helper functions

def grid_to_image(grid, scale=10):
    """Convert binary grid to RGB image."""
    # np.repeat(array, repeats, axis) duplicates elements along an axis
    # Here it enlarges each cell to a scale×scale block so we can see it
    gray = np.repeat(np.repeat(grid * 255, scale, axis=0), scale, axis=1)
    # np.stack() joins arrays along a new axis, creating 3 identical channels (grayscale RGB)
    return np.stack([gray, gray, gray], axis=2).astype(np.uint8)

def game_of_life_step(grid):
    """Apply one generation of Conway's Game of Life rules."""
    # np.array() creates the Moore neighborhood kernel (8-neighbor count)
    kernel = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
    # convolve() slides the kernel across every cell, summing neighbors
    neighbor_count = convolve(grid, kernel, mode='wrap')
    # Birth: dead cell + 3 neighbors → alive | Survival: alive + 2-3 neighbors → alive
    return ((neighbor_count == 3) | ((grid == 1) & (neighbor_count == 2))).astype(int)

# Step 2: Initialize grid with blinker pattern
# np.zeros() creates an array filled with zeros (all cells dead)
grid = np.zeros((30, 30), dtype=int)
grid[15, 14:17] = [1, 1, 1]  # Horizontal blinker in center

# Step 3: Evolve and observe
for generation in range(6):
    grid = game_of_life_step(grid)
    # np.sum() adds all elements, counting living cells (1s) in the grid
    print(f"Generation {generation + 1}: {np.sum(grid)} living cells")

# Step 4: Save result
Image.fromarray(grid_to_image(grid)).save('exercise1_result.png')
print("Saved exercise1_result.png")
