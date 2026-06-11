"""
interpolation_demo.py — render a 4-row comparison of one-dimensional
interpolation methods: nearest-neighbour, linear, cosine, and Catmull-Rom.
Each row connects the same five control points and shows how the choice
of interpolation rule shapes the in-between values.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image, ImageDraw


WIDTH, HEIGHT = 720, 480
ROW_HEIGHT = HEIGHT // 4
PADDING_X = 50
PADDING_Y = 30
PLOT_W = WIDTH - 2 * PADDING_X
PLOT_H = ROW_HEIGHT - 2 * PADDING_Y


KEYS = [0.1, 0.7, 0.3, 0.85, 0.45]   # five normalised heights
N_KEYS = len(KEYS)
N_SAMPLES = 256


def nearest(t, keys):
    n = len(keys)
    idx = np.clip(np.round(t * (n - 1)).astype(int), 0, n - 1)
    return np.array(keys)[idx]


def linear(t, keys):
    n = len(keys)
    pos = t * (n - 1)
    i0 = np.clip(np.floor(pos).astype(int), 0, n - 1)
    i1 = np.clip(i0 + 1, 0, n - 1)
    frac = pos - i0
    keys = np.array(keys)
    return keys[i0] * (1 - frac) + keys[i1] * frac


def cosine(t, keys):
    n = len(keys)
    pos = t * (n - 1)
    i0 = np.clip(np.floor(pos).astype(int), 0, n - 1)
    i1 = np.clip(i0 + 1, 0, n - 1)
    frac = pos - i0
    # cosine ease — smooth in/out without polynomial control points
    eased = (1 - np.cos(frac * np.pi)) / 2
    keys = np.array(keys)
    return keys[i0] * (1 - eased) + keys[i1] * eased


def catmull_rom(t, keys):
    """Catmull-Rom spline — passes through each control point with
    smooth tangents derived from neighbours."""
    keys = np.array(keys, dtype=np.float64)
    n = len(keys)
    pos = t * (n - 1)
    i1 = np.clip(np.floor(pos).astype(int), 0, n - 1)
    i0 = np.clip(i1 - 1, 0, n - 1)
    i2 = np.clip(i1 + 1, 0, n - 1)
    i3 = np.clip(i1 + 2, 0, n - 1)
    f = pos - i1
    p0, p1, p2, p3 = keys[i0], keys[i1], keys[i2], keys[i3]
    return 0.5 * (
        (2 * p1)
        + (-p0 + p2) * f
        + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f ** 2
        + (-p0 + 3 * p1 - 3 * p2 + p3) * f ** 3
    )


METHODS = [
    ('nearest-neighbour', nearest, (200, 130, 90)),
    ('linear', linear, (110, 200, 255)),
    ('cosine', cosine, (180, 130, 255)),
    ('Catmull-Rom spline', catmull_rom, (140, 230, 140)),
]


canvas = Image.new('RGB', (WIDTH, HEIGHT), (18, 20, 30))
draw = ImageDraw.Draw(canvas)

t = np.linspace(0, 1, N_SAMPLES)
key_xs = np.linspace(PADDING_X, WIDTH - PADDING_X, N_KEYS)

for row, (name, fn, color) in enumerate(METHODS):
    oy_top = row * ROW_HEIGHT + PADDING_Y
    oy_bot = oy_top + PLOT_H

    # Background frame
    draw.rectangle(
        [PADDING_X, oy_top, WIDTH - PADDING_X, oy_bot],
        outline=(45, 50, 65),
    )

    # Plot interpolated curve
    values = fn(t, KEYS)
    values = np.clip(values, 0, 1)
    pts = [
        (
            int(PADDING_X + ti * PLOT_W),
            int(oy_top + (1 - vi) * PLOT_H),
        )
        for ti, vi in zip(t, values)
    ]
    draw.line(pts, fill=color, width=2)

    # Mark control points
    for kx, ky in zip(key_xs, KEYS):
        draw.ellipse(
            [kx - 5, oy_top + (1 - ky) * PLOT_H - 5,
             kx + 5, oy_top + (1 - ky) * PLOT_H + 5],
            fill=(240, 240, 250), outline=(80, 80, 100),
        )

    # Label
    draw.text((PADDING_X + 8, oy_top + 6), name, fill=color)


canvas.save('interpolation_demo.png')
print(f"Saved interpolation_demo.png — {len(METHODS)} methods on {N_KEYS} keys")
