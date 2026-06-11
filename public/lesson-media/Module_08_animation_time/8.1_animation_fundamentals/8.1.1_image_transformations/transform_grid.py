"""
transform_grid.py — render all twelve transformations in a single 4x3 grid
image so the reader can scan the operator family at a glance.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image


a = np.array(Image.open('python_logo.png').convert('RGB'))
H, W, _ = a.shape

LABELS = [
    'original', 'dim', 'flip', 'green-killed',
    'rolled channels', 'noise', 'spaced noise', 'quadrants',
    'distance map', 'circle-masked', 'donut mask', 'donut-cropped',
]


def render_all(arr):
    H, W, _ = arr.shape
    yy, xx = np.mgrid[:H, :W]
    cy, cx = H // 2, W // 2
    circle = (xx - cx) ** 2 + (yy - cy) ** 2
    rng = np.random.default_rng(0)
    noise = rng.integers(0, 10, arr.shape)

    out = []
    out.append(arr)
    out.append(arr // 2)
    out.append(arr[:, ::-1])
    g = arr.copy(); g[:, :, 1] = 0
    out.append(g)

    roll = arr.copy()
    roll[:, :, 2] = np.roll(roll[:, :, 2], 25, axis=1)
    roll[:, :, 1] = np.roll(roll[:, :, 1], 50, axis=0)
    out.append(roll)

    out.append((arr.astype(np.int64) * noise // 10).clip(0, 255))
    spaced = arr.astype(np.int64).copy()
    spaced[::3, ::3] = (spaced[::3, ::3] * noise[::3, ::3]) // 10
    out.append(spaced.clip(0, 255))

    s = arr.copy()
    hh, hw = H // 2, W // 2
    s[hh:, hw:, 0] = 0; s[:hh, :hw, 1] = 0; s[:hh, hw:, 2] = 0
    out.append(s)

    # Convert single-channel images to 3-channel for the grid
    circle_3 = np.stack([(circle // 100).clip(0, 255)] * 3, axis=-1)
    out.append(circle_3)

    gc = arr.astype(np.int64).copy()
    for ch in range(3): gc[:, :, ch] = gc[:, :, ch] * circle
    out.append((gc // 20000).clip(0, 255))

    donut = np.logical_and(circle < 4500, circle > 3500)
    mask = 1 - donut.astype(np.int64)
    out.append(np.stack([(mask * 255).astype(np.int64)] * 3, axis=-1))

    g_donut = arr.astype(np.int64).copy()
    for ch in range(3): g_donut[:, :, ch] = g_donut[:, :, ch] * mask
    out.append(g_donut.clip(0, 255))

    return out


tiles = render_all(a)

# Composite into a 4x3 grid
rows, cols = 3, 4
gap = 8
gh, gw = H + gap, W + gap
canvas = np.full((rows * gh + gap, cols * gw + gap, 3), 28, dtype=np.uint8)
for i, t in enumerate(tiles):
    r, c = i // cols, i % cols
    canvas[gap + r * gh: gap + r * gh + H, gap + c * gw: gap + c * gw + W] = t.astype(np.uint8)

Image.fromarray(canvas).save('transform_grid.png')
print(f"Saved transform_grid.png — {len(tiles)} tiles in a {rows}x{cols} grid")
