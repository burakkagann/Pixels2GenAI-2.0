import numpy as np
from PIL import Image

def make_twinkling_starfield(seed, frame, n_stars=180, xsize=720, ysize=480):
    rng = np.random.default_rng(seed)
    field = np.zeros((ysize, xsize, 3), dtype=np.uint8)

    # TODO 1: generate star positions (same for all frames)
    # ys, xs, base_b = ...

    # TODO 2: per-frame brightness offset
    # twinkle = sin(frame * 2 * pi / 60 + phase_per_star) * 30
    # actual_b = clip(base_b + twinkle, 100, 255)

    # TODO 3: write stars at (ys, xs) with brightness actual_b
    return field
