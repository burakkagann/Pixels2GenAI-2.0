"""
star_polygon.py — connect every k-th vertex of a regular n-gon to draw a star
polygon (Schlafli symbol {n/k}). The classic five-pointed star is {5/2}.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image


def draw_line(canvas, x0, y0, x1, y1):
    n = max(abs(x1 - x0), abs(y1 - y0)) + 1
    xs = np.linspace(x0, x1, n).round().astype(int)
    ys = np.linspace(y0, y1, n).round().astype(int)
    canvas[ys, xs] = 255


def star_polygon(canvas, num_points, skip, cx, cy, radius):
    """Connect every `skip`-th vertex of an n-gon to draw a star polygon."""
    angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False) - np.pi / 2
    xs = (cx + radius * np.cos(angles)).astype(int)
    ys = (cy + radius * np.sin(angles)).astype(int)

    for i in range(num_points):
        x0, y0 = xs[i], ys[i]
        x1, y1 = xs[(i + skip) % num_points], ys[(i + skip) % num_points]
        draw_line(canvas, x0, y0, x1, y1)


CANVAS_SIZE = 400
canvas = np.zeros((CANVAS_SIZE, CANVAS_SIZE), dtype=np.uint8)

# {5/2} — classic five-pointed star
star_polygon(canvas, num_points=5, skip=2, cx=200, cy=200, radius=160)

Image.fromarray(canvas, mode='L').save('star_polygon.png')
