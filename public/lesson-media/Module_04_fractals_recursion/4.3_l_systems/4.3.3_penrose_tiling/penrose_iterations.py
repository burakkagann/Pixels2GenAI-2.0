"""
penrose_iterations.py — render the Penrose tiling at deflation depths
1 through 5, side by side, so the deflation process is visible step by
step. Each step subdivides every triangle, doubling/tripling the count;
by depth 5 the wheel looks like a finished aperiodic tiling.

Pixels2GenAI Project
"""

import math
import cmath
from PIL import Image, ImageDraw


PANEL = 280
GOLDEN = (1 + 5 ** 0.5) / 2


def subdivide(triangles):
    result = []
    for color, a, b, c in triangles:
        if color == 0:
            p = a + (b - a) / GOLDEN
            result.append((0, c, p, b))
            result.append((1, p, c, a))
        else:
            q = b + (a - b) / GOLDEN
            r = b + (c - b) / GOLDEN
            result.append((1, r, c, a))
            result.append((1, q, r, b))
            result.append((0, r, q, a))
    return result


def build_wheel():
    triangles = []
    for i in range(10):
        b = cmath.exp((2 * i + 1) * math.pi * 1j / 10)
        c = cmath.exp((2 * i - 1) * math.pi * 1j / 10)
        if i % 2 == 0:
            b, c = c, b
        triangles.append((0, 0 + 0j, b, c))
    return triangles


def render(triangles, size, scale):
    img = Image.new('RGB', size, (18, 20, 30))
    draw = ImageDraw.Draw(img)
    cx, cy = size[0] / 2, size[1] / 2
    for color, a, b, c in triangles:
        pts = [(cx + scale * z.real, cy + scale * z.imag) for z in (a, b, c)]
        fill = (210, 215, 90) if color == 0 else (255, 175, 90)
        draw.polygon(pts, fill=fill, outline=(40, 40, 55))
    return img


# Build five panels at depths 1..5 sharing the same canvas size
triangles = build_wheel()
panels = []
for depth in range(1, 6):
    triangles = subdivide(triangles)
    img = render(triangles, (PANEL, PANEL), PANEL * 0.42)
    ImageDraw.Draw(img).text((8, 8), f"n={depth} ({len(triangles)} tiles)",
                             fill=(220, 220, 230))
    panels.append(img)

grid = Image.new('RGB', (PANEL * 5, PANEL), (18, 20, 30))
for i, p in enumerate(panels):
    grid.paste(p, (i * PANEL, 0))
grid.save('penrose_iterations.png')
print('Saved penrose_iterations.png — deflation depths 1..5')
