"""
simple_penrose.py — generate a P3 Penrose rhombus tiling by deflation. Start
with ten "thin" Robinson triangles arranged in a wheel around the origin
(this approximates the central decagonal patch of the P3 tiling). Each
deflation step subdivides every triangle into smaller triangles according
to the Robinson production rules. Tiles are kept as oriented triangles in
complex-number coordinates; Pillow renders them filled in two colours.

After 5 deflation steps the wheel contains thousands of triangles arranged
in the characteristic 5-fold symmetric, non-repeating Penrose pattern.

Pixels2GenAI Project
"""

import math
import cmath
from PIL import Image, ImageDraw


SIZE = (800, 800)
ITERATIONS = 5
GOLDEN = (1 + 5 ** 0.5) / 2  # phi


def subdivide(triangles):
    """One deflation step. Each triangle splits into 2 (kite) or 3 (dart)."""
    result = []
    for color, a, b, c in triangles:
        if color == 0:
            # 0 = "thin" Robinson triangle, splits into 1 thin + 1 thick
            p = a + (b - a) / GOLDEN
            result.append((0, c, p, b))
            result.append((1, p, c, a))
        else:
            # 1 = "thick" Robinson triangle, splits into 1 thin + 2 thick
            q = b + (a - b) / GOLDEN
            r = b + (c - b) / GOLDEN
            result.append((1, r, c, a))
            result.append((1, q, r, b))
            result.append((0, r, q, a))
    return result


# Build the initial "wheel" of 10 thin triangles around the origin
triangles = []
for i in range(10):
    b = cmath.exp((2 * i + 1) * math.pi * 1j / 10)
    c = cmath.exp((2 * i - 1) * math.pi * 1j / 10)
    if i % 2 == 0:
        b, c = c, b
    triangles.append((0, 0 + 0j, b, c))

# Deflate
for _ in range(ITERATIONS):
    triangles = subdivide(triangles)
print(f"Tile count after {ITERATIONS} deflations: {len(triangles)}")

# Render. Scale the unit-radius wheel to fit the canvas.
scale = min(SIZE) * 0.45
cx, cy = SIZE[0] / 2, SIZE[1] / 2
img = Image.new('RGB', SIZE, (18, 20, 30))
draw = ImageDraw.Draw(img)

for color, a, b, c in triangles:
    pts = [(cx + scale * z.real, cy + scale * z.imag) for z in (a, b, c)]
    fill = (210, 215, 90) if color == 0 else (255, 175, 90)
    draw.polygon(pts, fill=fill, outline=(40, 40, 55))

img.save('simple_penrose.png')
print('Saved simple_penrose.png')
