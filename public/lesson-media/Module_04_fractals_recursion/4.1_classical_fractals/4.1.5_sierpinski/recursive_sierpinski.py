"""
recursive_sierpinski.py — same gasket, generated recursively. At each depth,
the triangle is divided into four smaller copies; we draw the central
upside-down triangle by leaving it blank and recurse into the three corners.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image
from PIL.ImageDraw import Draw


SIZE = 600


def midpoint(a, b):
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)


def draw_sierpinski(canvas, p1, p2, p3, depth, color=(255, 220, 110)):
    """Recursively fill the three corner sub-triangles at decreasing scale."""
    if depth == 0:
        Draw(canvas).polygon([p1, p2, p3], fill=color)
        return

    # Midpoints of each edge form the central (inverted) triangle we leave blank.
    m12 = midpoint(p1, p2)
    m23 = midpoint(p2, p3)
    m13 = midpoint(p1, p3)

    # Recurse into the three corner triangles.
    draw_sierpinski(canvas, p1,  m12, m13, depth - 1, color)
    draw_sierpinski(canvas, m12, p2,  m23, depth - 1, color)
    draw_sierpinski(canvas, m13, m23, p3,  depth - 1, color)


# Equilateral triangle vertices for the outer hull.
p_top = (SIZE * 0.5, SIZE * 0.10)
p_bl  = (SIZE * 0.10, SIZE * 0.85)
p_br  = (SIZE * 0.90, SIZE * 0.85)

canvas = Image.new('RGB', (SIZE, SIZE), color=(20, 20, 30))
draw_sierpinski(canvas, p_top, p_bl, p_br, depth=6)
canvas.save('recursive_sierpinski.png')
print(f"Saved recursive_sierpinski.png — depth 6, {3 ** 6} solid sub-triangles")
