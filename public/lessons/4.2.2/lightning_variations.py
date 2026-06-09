"""
lightning_variations.py — render four bolts side-by-side with different
displacement-decay parameters, showing how the 'roughness' exponent shapes
the bolt's character. Low decay = persistent jaggedness at every scale.
High decay = clean spine with only small jitter.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image, ImageDraw


TILE = (300, 600)
DECAYS = [0.4, 0.5, 0.6, 0.75]
LABELS = ['decay 0.40', 'decay 0.50', 'decay 0.60', 'decay 0.75']


def midpoint_bolt(start, end, displacement, depth, decay, rng):
    if depth == 0:
        return [start, end]
    mid = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = (dx * dx + dy * dy) ** 0.5 or 1.0
    nx, ny = -dy / length, dx / length
    offset = rng.uniform(-displacement, displacement)
    mid_p = (mid[0] + nx * offset, mid[1] + ny * offset)
    left  = midpoint_bolt(start, mid_p, displacement * decay, depth - 1, decay, rng)
    right = midpoint_bolt(mid_p, end,   displacement * decay, depth - 1, decay, rng)
    return left + right[1:]


grid = Image.new('RGB', (TILE[0] * 4, TILE[1]), color=(6, 8, 22))
draw = ImageDraw.Draw(grid)

rng = np.random.default_rng(42)
for i, decay in enumerate(DECAYS):
    x_offset = i * TILE[0]
    start = (x_offset + TILE[0] / 2, 30)
    end   = (x_offset + TILE[0] / 2, TILE[1] - 30)
    points = midpoint_bolt(start, end, displacement=110, depth=8,
                           decay=decay, rng=rng)
    draw.line(points, fill=(170, 215, 255), width=2)

grid.save('lightning_variations.png')
print(f"Saved lightning_variations.png — decays {DECAYS}")
