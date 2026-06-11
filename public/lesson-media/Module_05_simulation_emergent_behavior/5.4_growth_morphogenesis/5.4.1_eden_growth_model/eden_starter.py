"""
eden_starter.py - Exercise 3 scaffold.

Setup and rendering are wired up. You implement `grow_one()` - one step
of perimeter-list growth.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image
import imageio.v2 as imageio
import matplotlib

GRID = 220
SCALE = 2
NUM_FRAMES = 50
STEPS_PER_FRAME = 200
FPS = 18


def grow_one(grid, ages, perimeter, age, rng):
    """TODO: implement one step of Eden growth.

    1. If perimeter is empty, return.
    2. Pick a uniformly random index into perimeter.
    3. Remove that entry (use swap-remove for O(1) cost).
    4. Mark that cell occupied in grid; record its age in ages.
    5. For each of its 4 neighbours that is in-bounds and not yet occupied,
       append the neighbour coordinate to perimeter.
    """
    pass


def render(grid, ages):
    cmap = matplotlib.colormaps['magma']
    norm = ages / max(ages.max(), 1)
    img = (cmap(norm)[..., :3] * 255).astype(np.uint8)
    img[~grid] = (8, 6, 14)
    return np.repeat(np.repeat(img, SCALE, axis=0), SCALE, axis=1)


def main():
    rng = np.random.default_rng(0)
    grid = np.zeros((GRID, GRID), dtype=bool)
    ages = np.zeros((GRID, GRID), dtype=np.int32)
    c = GRID // 2
    grid[c, c] = True
    ages[c, c] = 1
    perimeter = [(c - 1, c), (c + 1, c), (c, c - 1), (c, c + 1)]
    age = 1
    frames = []
    for _ in range(NUM_FRAMES):
        for _ in range(STEPS_PER_FRAME):
            age += 1
            grow_one(grid, ages, perimeter, age, rng)
        frames.append(render(grid, ages))
    imageio.mimsave('eden_starter.gif', frames, fps=FPS)


if __name__ == '__main__':
    main()
