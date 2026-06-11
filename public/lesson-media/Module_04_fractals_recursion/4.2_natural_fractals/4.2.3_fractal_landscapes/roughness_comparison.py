"""
roughness_comparison.py — render four heightmaps side by side at
different roughness values to show how a single parameter shifts the
terrain from rolling hills to jagged mountains.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image, ImageDraw


N, SIZE = 8, 2 ** 8 + 1
ROUGHNESS_VALUES = [0.40, 0.50, 0.60, 0.70]


def diamond_square(size, roughness, seed):
    rng = np.random.default_rng(seed)
    h = np.zeros((size, size), dtype=np.float64)
    h[0, 0]                 = rng.uniform(-1, 1)
    h[0, size - 1]          = rng.uniform(-1, 1)
    h[size - 1, 0]          = rng.uniform(-1, 1)
    h[size - 1, size - 1]   = rng.uniform(-1, 1)
    step = size - 1
    scale = 1.0
    while step > 1:
        half = step // 2
        for y in range(half, size - 1, step):
            for x in range(half, size - 1, step):
                avg = (h[y - half, x - half] + h[y - half, x + half]
                       + h[y + half, x - half] + h[y + half, x + half]) / 4.0
                h[y, x] = avg + rng.uniform(-scale, scale)
        for y in range(0, size, half):
            x_start = 0 if (y // half) % 2 == 1 else half
            for x in range(x_start, size, step):
                neigh = []
                if x - half >= 0:    neigh.append(h[y, x - half])
                if x + half < size:  neigh.append(h[y, x + half])
                if y - half >= 0:    neigh.append(h[y - half, x])
                if y + half < size:  neigh.append(h[y + half, x])
                h[y, x] = sum(neigh) / len(neigh) + rng.uniform(-scale, scale)
        step //= 2
        scale *= roughness
    h -= h.min()
    h /= max(h.max(), 1e-9)
    return h


# Generate four heightmaps using the same seed so the differences come purely
# from the roughness parameter.
maps = [diamond_square(SIZE, r, seed=2025) for r in ROUGHNESS_VALUES]

# Tile horizontally
grid = np.zeros((SIZE, SIZE * 4), dtype=np.uint8)
for i, h in enumerate(maps):
    grid[:, i * SIZE:(i + 1) * SIZE] = (h * 255).astype(np.uint8)

Image.fromarray(grid, mode='L').save('roughness_comparison.png')
print(f"Saved roughness_comparison.png — roughnesses {ROUGHNESS_VALUES}")
