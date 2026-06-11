"""
meanshift_starter.py - Exercise scaffold for Mean-Shift segmentation.

Image generation and rendering are wired up. You implement
`mean_shift_step()` - one Mean-Shift iteration on a single seed point.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image

WIDTH, HEIGHT = 280, 200
NUM_SEEDS = 12
NUM_ITERS = 25
BANDWIDTH = 35.0


def mean_shift_step(seed, points, bandwidth):
    """TODO: return the next position of `seed` after one Mean-Shift step.

    1. Compute the distance from `seed` to every point.
    2. Build a mask of points within `bandwidth` of `seed`.
    3. Return the mean of the masked points. (If no points are in range,
       return seed unchanged.)
    """
    return seed


def synthesise_input(w, h):
    img = np.full((h, w, 3), 30, dtype=np.uint8)
    img[40:90, 50:120] = (220, 80, 90)
    img[40:90, 160:230] = (250, 200, 60)
    img[120:170, 90:200] = (90, 200, 140)
    return img


def main():
    image = synthesise_input(WIDTH, HEIGHT)
    pixels = image.reshape(-1, 3).astype(np.float32)
    rng = np.random.default_rng(0)
    seed_idx = rng.choice(len(pixels), size=NUM_SEEDS, replace=False)
    seeds = pixels[seed_idx].copy()

    for _ in range(NUM_ITERS):
        for i, s in enumerate(seeds):
            seeds[i] = mean_shift_step(s, pixels, BANDWIDTH)

    # Snap each pixel to its nearest converged seed
    dist = np.linalg.norm(pixels[:, None] - seeds[None, :], axis=-1)
    labels = dist.argmin(axis=1)
    out = seeds[labels].clip(0, 255).astype(np.uint8).reshape(HEIGHT, WIDTH, 3)
    Image.fromarray(out).save('meanshift_starter.png')
    print('Wrote meanshift_starter.png')


if __name__ == '__main__':
    main()
