"""
polygon_variations.py — six regular polygons in one panel: triangle, square,
pentagon, hexagon, octagon, dodecagon. As n grows the silhouette converges to
the circle.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image


def draw_line(canvas, x0, y0, x1, y1):
    n = max(abs(x1 - x0), abs(y1 - y0)) + 1
    xs = np.linspace(x0, x1, n).round().astype(int)
    ys = np.linspace(y0, y1, n).round().astype(int)
    canvas[ys, xs] = 255


def draw_polygon(canvas, num_sides, cx, cy, radius, rotation=-np.pi / 2):
    angles = np.linspace(0, 2 * np.pi, num_sides, endpoint=False) + rotation
    xs = (cx + radius * np.cos(angles)).astype(int)
    ys = (cy + radius * np.sin(angles)).astype(int)
    vertices = list(zip(xs, ys))
    for (x0, y0), (x1, y1) in zip(vertices, vertices[1:] + vertices[:1]):
        draw_line(canvas, x0, y0, x1, y1)


CANVAS_W, CANVAS_H = 600, 400
canvas = np.zeros((CANVAS_H, CANVAS_W), dtype=np.uint8)

# Layout: two rows of three polygons
positions = [(100, 100), (300, 100), (500, 100),
             (100, 300), (300, 300), (500, 300)]
sides = [3, 4, 5, 6, 8, 12]

for (cx, cy), n in zip(positions, sides):
    draw_polygon(canvas, n, cx, cy, radius=75)

Image.fromarray(canvas, mode='L').save('polygon_variations.png')
