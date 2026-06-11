"""
simple_heightmap.py — generate a fractal heightmap with the diamond-square
algorithm. Start with random heights at the four corners of a (2^n + 1)-square
grid. At every iteration, halve the cell size, and:
  - DIAMOND step: each diamond centre is the average of its four corner
    heights, plus random jitter.
  - SQUARE step: each square centre is the average of its four diamond
    midpoints, plus random jitter.
The jitter scale shrinks geometrically by `roughness`. Output is a grayscale
heightmap that looks like mountain terrain seen from above.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image


N = 9                       # grid size will be 2^N + 1 = 513
SIZE = 2 ** N + 1
ROUGHNESS = 0.55            # smaller = smoother; larger = rougher
SEED = 1


def diamond_square(size, roughness, seed):
    """Return a (size, size) heightmap with values in [0, 1]."""
    assert (size - 1) & (size - 2) == 0, "size must be 2^k + 1"

    rng = np.random.default_rng(seed)
    h = np.zeros((size, size), dtype=np.float64)

    # Seed the four corners
    h[0, 0]              = rng.uniform(-1, 1)
    h[0, size - 1]       = rng.uniform(-1, 1)
    h[size - 1, 0]       = rng.uniform(-1, 1)
    h[size - 1, size - 1] = rng.uniform(-1, 1)

    step = size - 1
    scale = 1.0

    while step > 1:
        half = step // 2

        # DIAMOND step — centre of each square is the average of 4 corners + jitter
        for y in range(half, size - 1, step):
            for x in range(half, size - 1, step):
                avg = (h[y - half, x - half] + h[y - half, x + half]
                       + h[y + half, x - half] + h[y + half, x + half]) / 4.0
                h[y, x] = avg + rng.uniform(-scale, scale)

        # SQUARE step — midpoints of each edge are the average of 4 diamond neighbours + jitter
        # We treat edges by skipping out-of-bound neighbours and averaging only what exists.
        for y in range(0, size, half):
            x_start = 0 if (y // half) % 2 == 1 else half
            for x in range(x_start, size, step):
                neighbours = []
                if x - half >= 0:       neighbours.append(h[y, x - half])
                if x + half < size:     neighbours.append(h[y, x + half])
                if y - half >= 0:       neighbours.append(h[y - half, x])
                if y + half < size:     neighbours.append(h[y + half, x])
                h[y, x] = sum(neighbours) / len(neighbours) + rng.uniform(-scale, scale)

        step //= 2
        scale *= roughness

    # Renormalise to [0, 1]
    h -= h.min()
    h /= max(h.max(), 1e-9)
    return h


heightmap = diamond_square(SIZE, ROUGHNESS, SEED)

# Render as grayscale terrain seen from above
img8 = (heightmap * 255).astype(np.uint8)
Image.fromarray(img8, mode='L').save('simple_heightmap.png')
print(f"Saved simple_heightmap.png — {SIZE}x{SIZE}, roughness {ROUGHNESS}")
