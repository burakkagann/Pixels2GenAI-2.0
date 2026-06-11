"""
eden_growth.py - The Eden growth model. Start with a single occupied cell.
Each iteration, find every empty cell adjacent to an occupied one (the
"perimeter"), pick one uniformly at random, and occupy it. The colony
grows into a rough disc with a characteristic rough boundary.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image
import imageio.v2 as imageio

# ---------- CONFIG ----------
GRID = 240
SCALE = 2
NUM_FRAMES = 60
STEPS_PER_FRAME = 220       # how many cells to add between rendered frames
FPS = 18

PALETTE_NAME = 'magma'      # matplotlib colormap
BG = (8, 6, 14)
# ----------------------------


def neighbours(r, c):
    return [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]


def grow_one(grid, ages, perimeter, age, rng):
    if not perimeter:
        return
    idx = rng.integers(0, len(perimeter))
    r, c = perimeter[idx]
    perimeter[idx] = perimeter[-1]
    perimeter.pop()
    grid[r, c] = True
    ages[r, c] = age
    for nr, nc in neighbours(r, c):
        if 0 <= nr < GRID and 0 <= nc < GRID and not grid[nr, nc]:
            perimeter.append((nr, nc))


def render(grid, ages):
    import matplotlib as mpl
    cmap = mpl.colormaps[PALETTE_NAME]
    max_age = max(ages.max(), 1)
    norm = ages / max_age
    img = (cmap(norm)[..., :3] * 255).astype(np.uint8)
    img[~grid] = BG
    return np.repeat(np.repeat(img, SCALE, axis=0), SCALE, axis=1)


def main():
    rng = np.random.default_rng(42)
    grid = np.zeros((GRID, GRID), dtype=bool)
    ages = np.zeros((GRID, GRID), dtype=np.int32)
    cx = cy = GRID // 2
    grid[cy, cx] = True
    ages[cy, cx] = 1
    perimeter = []
    for nr, nc in neighbours(cy, cx):
        perimeter.append((nr, nc))

    age = 1
    frames = []
    for frame in range(NUM_FRAMES):
        for _ in range(STEPS_PER_FRAME):
            age += 1
            grow_one(grid, ages, perimeter, age, rng)
        frames.append(render(grid, ages))
        if frame == NUM_FRAMES - 1:
            Image.fromarray(frames[-1]).save('eden_final.png')

    imageio.mimsave('eden_growth.gif', frames, fps=FPS)
    print(f'Wrote eden_growth.gif ({NUM_FRAMES} frames; total cells {grid.sum()})')


if __name__ == '__main__':
    main()
