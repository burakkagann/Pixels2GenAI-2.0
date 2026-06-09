"""
lissajous_variations.py — a six-panel grid of Lissajous curves with different
frequency ratios. Closed shapes occur when a/b is rational; the figure's
visible "number of lobes" along each axis equals the other frequency.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image


def draw_polyline(canvas, xs, ys, color=255):
    h, w = canvas.shape[:2]
    xi = np.round(xs).astype(int)
    yi = np.round(ys).astype(int)
    inside = (xi >= 0) & (xi < w) & (yi >= 0) & (yi < h)
    canvas[yi[inside], xi[inside]] = color


PANEL = 200
CANVAS_W, CANVAS_H = PANEL * 3, PANEL * 2
canvas = np.zeros((CANVAS_H, CANVAS_W), dtype=np.uint8)

# Six (a, b, delta) combinations
configs = [
    (1, 2, np.pi / 2),    # parabolic figure-eight
    (1, 3, np.pi / 2),    # three-lobe
    (2, 3, np.pi / 2),    # classic 2:3
    (3, 4, np.pi / 4),    # 3:4 with shifted phase
    (3, 5, np.pi / 2),    # five-by-three
    (5, 7, np.pi / 2),    # higher-order coprime
]

amplitude = PANEL // 2 - 12
t = np.linspace(0, 2 * np.pi, 6000)

for idx, (a, b, delta) in enumerate(configs):
    col = idx % 3
    row = idx // 3
    cx = col * PANEL + PANEL // 2
    cy = row * PANEL + PANEL // 2

    xs = cx + amplitude * np.sin(a * t + delta)
    ys = cy + amplitude * np.sin(b * t)
    draw_polyline(canvas, xs, ys)

Image.fromarray(canvas, mode='L').save('lissajous_variations.png')
