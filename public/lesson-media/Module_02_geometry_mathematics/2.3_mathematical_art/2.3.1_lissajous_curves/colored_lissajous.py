"""
colored_lissajous.py — a Lissajous curve coloured by progress along the path.

The hue cycles through the full colour wheel as t sweeps through a single
period, giving a coloured ribbon that highlights how the curve closes on
itself.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image


def hue_to_rgb(hue):
    """Map hue in [0, 1] to RGB via the 6-segment HSV wheel."""
    h6 = hue * 6
    c = np.ones_like(h6); z = np.zeros_like(h6)
    x = 1 - np.abs((h6 % 2) - 1)
    seg = h6.astype(int) % 6
    r = np.choose(seg, [c, x, z, z, x, c])
    g = np.choose(seg, [x, c, c, x, z, z])
    b = np.choose(seg, [z, z, x, c, c, x])
    return (np.stack([r, g, b], axis=-1) * 255).astype(np.uint8)


CANVAS_SIZE = 512
canvas = np.zeros((CANVAS_SIZE, CANVAS_SIZE, 3), dtype=np.uint8)

amplitude = 220
a, b = 5, 6
delta = np.pi / 2

num_points = 6000
t = np.linspace(0, 2 * np.pi, num_points)
xs = CANVAS_SIZE / 2 + amplitude * np.sin(a * t + delta)
ys = CANVAS_SIZE / 2 + amplitude * np.sin(b * t)

# Progress in [0, 1] along the curve, mapped to hue
progress = np.linspace(0, 1, num_points)
colors = hue_to_rgb(progress)

xi = np.round(xs).astype(int)
yi = np.round(ys).astype(int)
inside = (xi >= 0) & (xi < CANVAS_SIZE) & (yi >= 0) & (yi < CANVAS_SIZE)

canvas[yi[inside], xi[inside]] = colors[inside]

Image.fromarray(canvas, mode='RGB').save('colored_lissajous.png')
