"""
colored_penrose.py — same deflation algorithm as simple_penrose.py but with
a palette that highlights both the 5-fold symmetry of the central decagonal
patch and the local Penrose patches (the "Sun" and "Star" configurations
that appear scattered through any P3 tiling).

Tiles are coloured by their distance from the centre, with subtle hue
shifts based on type (thin vs thick rhombus). The result is a print-ready
visual demonstration of how aperiodicity coexists with strong local order.

Pixels2GenAI Project
"""

import math
import cmath
from PIL import Image, ImageDraw


SIZE = (900, 900)
ITERATIONS = 5
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


triangles = []
for i in range(10):
    b = cmath.exp((2 * i + 1) * math.pi * 1j / 10)
    c = cmath.exp((2 * i - 1) * math.pi * 1j / 10)
    if i % 2 == 0:
        b, c = c, b
    triangles.append((0, 0 + 0j, b, c))

for _ in range(ITERATIONS):
    triangles = subdivide(triangles)
print(f"Tile count: {len(triangles)}")

scale = min(SIZE) * 0.46
cx, cy = SIZE[0] / 2, SIZE[1] / 2
img = Image.new('RGB', SIZE, (12, 14, 28))
draw = ImageDraw.Draw(img)


def palette(color, dist):
    """Distance-based palette with a subtle thin/thick hue shift."""
    if color == 0:  # thin rhombus tile
        r = int(80 + 175 * dist)
        g = int(220 - 80 * dist)
        b = int(180 - 60 * dist)
    else:           # thick rhombus tile
        r = int(255 - 50 * dist)
        g = int(160 - 80 * dist)
        b = int(80 + 90 * dist)
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))


for color, a, b, c in triangles:
    centroid = (a + b + c) / 3
    dist = min(1.0, abs(centroid))
    pts = [(cx + scale * z.real, cy + scale * z.imag) for z in (a, b, c)]
    draw.polygon(pts, fill=palette(color, dist), outline=(40, 40, 55))

img.save('colored_penrose.png')
print('Saved colored_penrose.png')
