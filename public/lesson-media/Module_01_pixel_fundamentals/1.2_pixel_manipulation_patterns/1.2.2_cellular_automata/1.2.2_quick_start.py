import numpy as np
from PIL import Image
from scipy.ndimage import convolve
import imageio

def grid_to_image(grid, scale=8):
    """Convert binary grid to grayscale image."""
    return np.repeat(np.repeat(grid * 255, scale, axis=0), scale, axis=1).astype(np.uint8)

grid = np.zeros((20, 20), dtype=int)
grid[8:11, 8:11] = [[0, 1, 0], [0, 0, 1], [1, 1, 1]]  # Glider

# Moore neighbourhood kernel (counts 8 surrounding cells, excludes centre)
kernel = np.array([[1, 1, 1],
                   [1, 0, 1],
                   [1, 1, 1]])

frames = []
for step in range(8):
    frames.append(grid_to_image(grid))
    neighbor_count = convolve(grid, kernel, mode='wrap')
    # Apply B3/S23 rules
    birth = (neighbor_count == 3)
    survival = (grid == 1) & (neighbor_count == 2)
    grid = (birth | survival).astype(int)

imageio.mimsave('glider_animation.gif', frames, fps=2, duration=0.5)
