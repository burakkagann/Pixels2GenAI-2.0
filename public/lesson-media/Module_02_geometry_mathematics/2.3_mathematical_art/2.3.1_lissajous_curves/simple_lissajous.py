"""
simple_lissajous.py — draw a Lissajous curve with frequencies a=3, b=4 and a
small phase shift. Two independent sinusoids, one driving x and one driving y;
the curve is the locus of their joint values as t sweeps through a full period.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image


def draw_polyline(canvas, xs, ys, color=255):
    """Plot xs/ys onto canvas at integer coordinates, clipping to bounds."""
    h, w = canvas.shape[:2]
    xi = np.round(xs).astype(int)
    yi = np.round(ys).astype(int)
    inside = (xi >= 0) & (xi < w) & (yi >= 0) & (yi < h)
    canvas[yi[inside], xi[inside]] = color


CANVAS_SIZE = 512
canvas = np.zeros((CANVAS_SIZE, CANVAS_SIZE), dtype=np.uint8)

# Lissajous parameters: x(t) = A sin(a t + delta), y(t) = B sin(b t)
amplitude = 220
a, b = 3, 4
delta = np.pi / 2     # quarter-cycle phase offset

t = np.linspace(0, 2 * np.pi, 4000)
xs = CANVAS_SIZE / 2 + amplitude * np.sin(a * t + delta)
ys = CANVAS_SIZE / 2 + amplitude * np.sin(b * t)

draw_polyline(canvas, xs, ys)

Image.fromarray(canvas, mode='L').save('simple_lissajous.png')
