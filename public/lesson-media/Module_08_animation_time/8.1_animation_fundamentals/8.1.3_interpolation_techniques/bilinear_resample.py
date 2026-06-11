"""
bilinear_resample.py — upsample a tiny 16x16 RGB pattern to 320x320 with
nearest-neighbour vs. bilinear interpolation, shown side by side.
The same idea drives every image-resize operation, and demonstrates
the 2D extension of linear interpolation.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image


SRC_SIZE = 16
DST_SIZE = 320

rng = np.random.default_rng(11)
src = rng.integers(0, 256, (SRC_SIZE, SRC_SIZE, 3), dtype=np.uint8)
# Make the colours saturated for visual clarity
src = (src.astype(np.float32) * 0.85 + 30).clip(0, 255).astype(np.uint8)


def nearest_neighbour(src, dst_size):
    sh, sw = src.shape[:2]
    # For each output pixel (y, x), find nearest source pixel
    yy = (np.arange(dst_size) * sh / dst_size).astype(int)
    xx = (np.arange(dst_size) * sw / dst_size).astype(int)
    yi, xi = np.meshgrid(yy, xx, indexing='ij')
    return src[yi, xi]


def bilinear(src, dst_size):
    sh, sw = src.shape[:2]
    # For each output pixel, find the four neighbouring source pixels and
    # linearly blend by the fractional position.
    src_f = src.astype(np.float32)
    y_pos = np.arange(dst_size) * (sh - 1) / (dst_size - 1)
    x_pos = np.arange(dst_size) * (sw - 1) / (dst_size - 1)

    y0 = np.floor(y_pos).astype(int)
    x0 = np.floor(x_pos).astype(int)
    y1 = np.clip(y0 + 1, 0, sh - 1)
    x1 = np.clip(x0 + 1, 0, sw - 1)
    dy = (y_pos - y0).astype(np.float32)[:, None]
    dx = (x_pos - x0).astype(np.float32)[None, :]

    Y0, X0 = np.meshgrid(y0, x0, indexing='ij')
    Y0, X1 = np.meshgrid(y0, x1, indexing='ij')
    Y1_, X0_ = np.meshgrid(y1, x0, indexing='ij')
    Y1, X1 = np.meshgrid(y1, x1, indexing='ij')

    # Bilinear blend: (1-dy)(1-dx) TL + (1-dy)dx TR + dy(1-dx) BL + dy*dx BR
    tl = src_f[Y0, X0]
    tr = src_f[Y0, X1]
    bl = src_f[Y1_, X0_]
    br = src_f[Y1, X1]

    out = (
        (1 - dy[..., None]) * (1 - dx[..., None]) * tl
        + (1 - dy[..., None]) * dx[..., None] * tr
        + dy[..., None] * (1 - dx[..., None]) * bl
        + dy[..., None] * dx[..., None] * br
    )
    return out.clip(0, 255).astype(np.uint8)


nn = nearest_neighbour(src, DST_SIZE)
bl = bilinear(src, DST_SIZE)

# Composite the two outputs side by side with a small gap
GAP = 16
canvas = np.full((DST_SIZE, DST_SIZE * 2 + GAP, 3), 22, dtype=np.uint8)
canvas[:, :DST_SIZE] = nn
canvas[:, DST_SIZE + GAP:] = bl

Image.fromarray(canvas).save('bilinear_resample.png')
print(f"Saved bilinear_resample.png — left: nearest, right: bilinear")
