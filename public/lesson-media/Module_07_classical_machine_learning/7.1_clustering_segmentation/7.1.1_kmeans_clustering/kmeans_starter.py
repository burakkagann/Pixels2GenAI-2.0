"""
kmeans_starter.py - Exercise / Synthesis scaffold.

The image generation and rendering are wired up. You implement
`kmeans_from_scratch()` - Lloyd's algorithm, no sklearn.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image, ImageDraw

WIDTH, HEIGHT = 320, 220
N_CLUSTERS = 5
NUM_ITERS = 12
RANDOM_STATE = 0


def kmeans_from_scratch(pixels, k, num_iters, rng):
    """TODO: implement Lloyd's algorithm.

    1. Initialise k centres by sampling k pixels uniformly at random
       (without replacement) — these are the seed centroids.
    2. Loop num_iters times:
       a. ASSIGN: for each pixel, find the index of the closest centre.
       b. UPDATE: for each cluster index c, set centre[c] to the mean of
          the pixels assigned to it (skip clusters with no members).
    3. Return centres (k, 3) and final labels (n_pixels,) as np arrays.
    """
    return np.zeros((k, 3)), np.zeros(len(pixels), dtype=int)


def synthesise_input(w, h):
    ys, xs = np.meshgrid(np.linspace(0, 1, h), np.linspace(0, 1, w), indexing='ij')
    r = 0.5 + 0.5 * np.cos(2 * np.pi * (xs * 1.3 + ys))
    g = 0.5 + 0.5 * np.sin(2 * np.pi * (xs - ys * 1.1))
    b = 0.5 + 0.5 * np.cos(2 * np.pi * (xs * 0.6 + ys * 1.8))
    img = np.stack([r, g, b], axis=-1) * 255
    return img.astype(np.uint8)


def main():
    rng = np.random.default_rng(RANDOM_STATE)
    image = synthesise_input(WIDTH, HEIGHT)
    pixels = image.reshape(-1, 3).astype(np.float32)

    centres, labels = kmeans_from_scratch(pixels, N_CLUSTERS, NUM_ITERS, rng)
    out_pixels = centres[labels].clip(0, 255).astype(np.uint8)
    out = out_pixels.reshape(HEIGHT, WIDTH, 3)
    Image.fromarray(out).save('kmeans_starter_output.png')
    print('Wrote kmeans_starter_output.png')


if __name__ == '__main__':
    main()
