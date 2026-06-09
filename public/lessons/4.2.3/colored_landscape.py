"""
colored_landscape.py — same diamond-square heightmap, but rendered as a
biome map. Each height band gets a colour: deep blue water, beach sand,
green forest, brown rock, white snow. The result is an instant top-down
illustration of a fractal continent.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image

# Reuse the diamond-square routine from simple_heightmap.py by import-equivalent
# inline copy (keeps each script self-contained).

N, ROUGHNESS, SEED = 9, 0.55, 4
SIZE = 2 ** N + 1


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


def biome_colour(h):
    """Map a heightmap in [0, 1] to RGB biome colours."""
    rgb = np.zeros(h.shape + (3,), dtype=np.uint8)
    water_deep   = (h < 0.32)
    water_shallow = (h >= 0.32) & (h < 0.42)
    sand          = (h >= 0.42) & (h < 0.48)
    grass         = (h >= 0.48) & (h < 0.65)
    forest        = (h >= 0.65) & (h < 0.78)
    rock          = (h >= 0.78) & (h < 0.90)
    snow          = (h >= 0.90)

    rgb[water_deep]     = (18,  48, 100)
    rgb[water_shallow]  = (52, 105, 160)
    rgb[sand]           = (210, 200, 140)
    rgb[grass]          = (90, 150,  80)
    rgb[forest]         = (50,  95,  55)
    rgb[rock]           = (115, 105,  95)
    rgb[snow]           = (245, 245, 250)
    return rgb


h = diamond_square(SIZE, ROUGHNESS, SEED)
rgb = biome_colour(h)
Image.fromarray(rgb, mode='RGB').save('colored_landscape.png')
print(f"Saved colored_landscape.png — {SIZE}x{SIZE}, roughness {ROUGHNESS}")
