"""
colored_attractor.py — Clifford attractor coloured by visitation order.

Each iteration of the Clifford map is assigned a hue based on how far into the
600 000-step sequence it was visited. Earlier points are red, later points are
purple. The colour overlay reveals how the attractor is *visited*, not just
its silhouette.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image


CANVAS_SIZE = 600
NUM_POINTS = 600_000

# Clifford attractor parameters
a, b, c, d = -1.7, 1.8, -1.9, -0.4


def to_pixel(v, low=-2.5, high=2.5):
    return int((v - low) / (high - low) * (CANVAS_SIZE - 1))


def hue_to_rgb_vec(hue):
    """Hue in [0, 1] → uint8 RGB triple."""
    h6 = hue * 6
    seg = int(h6) % 6
    x = 1 - abs((h6 % 2) - 1)
    table = [
        (1, x, 0), (x, 1, 0), (0, 1, x),
        (0, x, 1), (x, 0, 1), (1, 0, x),
    ]
    r, g, b = table[seg]
    return int(r * 255), int(g * 255), int(b * 255)


canvas = np.zeros((CANVAS_SIZE, CANVAS_SIZE, 3), dtype=np.uint8)

x, y = 0.1, 0.1
# Burn-in
for _ in range(100):
    x_new = np.sin(a * y) + c * np.cos(a * x)
    y_new = np.sin(b * x) + d * np.cos(b * y)
    x, y = x_new, y_new

for i in range(NUM_POINTS):
    x_new = np.sin(a * y) + c * np.cos(a * x)
    y_new = np.sin(b * x) + d * np.cos(b * y)
    x, y = x_new, y_new
    px, py = to_pixel(x), to_pixel(y)
    if 0 <= px < CANVAS_SIZE and 0 <= py < CANVAS_SIZE:
        progress = i / NUM_POINTS
        # Map progress into the warm-half of the colour wheel for a striking look
        hue = 0.05 + 0.7 * progress
        canvas[py, px] = hue_to_rgb_vec(hue)

Image.fromarray(canvas, mode='RGB').save('colored_attractor.png')
