"""
simple_polygon.py — draw a regular pentagon outline by sampling vertices on a
circle and connecting them with straight lines.

The pentagon is *never* drawn as a special primitive — it is five line segments
between five points on a unit circle, scaled and translated to the canvas.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image


def draw_line(canvas, x0, y0, x1, y1):
    """Rasterise a single line segment from (x0, y0) to (x1, y1)."""
    n = max(abs(x1 - x0), abs(y1 - y0)) + 1
    xs = np.linspace(x0, x1, n).round().astype(int)
    ys = np.linspace(y0, y1, n).round().astype(int)
    canvas[ys, xs] = 255


def polygon_vertices(num_sides, cx, cy, radius, rotation=-np.pi / 2):
    """Return num_sides (x, y) integer vertices on a circle of given radius."""
    angles = np.linspace(0, 2 * np.pi, num_sides, endpoint=False) + rotation
    xs = (cx + radius * np.cos(angles)).astype(int)
    ys = (cy + radius * np.sin(angles)).astype(int)
    return list(zip(xs, ys))


CANVAS_SIZE = 400
canvas = np.zeros((CANVAS_SIZE, CANVAS_SIZE), dtype=np.uint8)

vertices = polygon_vertices(num_sides=5, cx=200, cy=200, radius=160)

# Connect consecutive vertices; wrap around to close the shape
for (x0, y0), (x1, y1) in zip(vertices, vertices[1:] + vertices[:1]):
    draw_line(canvas, x0, y0, x1, y1)

Image.fromarray(canvas, mode='L').save('simple_polygon.png')
