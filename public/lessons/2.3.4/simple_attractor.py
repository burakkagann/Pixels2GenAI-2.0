"""
simple_attractor.py — render the de Jong attractor as a density-accumulated
point cloud.

The de Jong system is a non-linear discrete map that iterates a single point
through hundreds of thousands of steps. Every visited pixel increments a
density counter; the final image is the log-scaled density.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image


CANVAS_SIZE = 600
NUM_POINTS = 400_000

# de Jong attractor parameters (one of many possible quadruples)
a, b, c, d = 1.641, 1.902, 0.316, 1.525


def iterate_de_jong(x, y):
    """One step of the de Jong map: returns (x', y')."""
    return np.sin(a * y) - np.cos(b * x), np.sin(c * x) - np.cos(d * y)


# Iterate from a deterministic start point
x, y = 0.1, 0.1
density = np.zeros((CANVAS_SIZE, CANVAS_SIZE), dtype=np.uint32)

# The de Jong attractor lives roughly in [-2, 2] x [-2, 2]
def to_pixel(v):
    return int((v + 2) / 4 * (CANVAS_SIZE - 1))

# Burn in a few iterations so we land on the attractor
for _ in range(100):
    x, y = iterate_de_jong(x, y)

for _ in range(NUM_POINTS):
    x, y = iterate_de_jong(x, y)
    px, py = to_pixel(x), to_pixel(y)
    if 0 <= px < CANVAS_SIZE and 0 <= py < CANVAS_SIZE:
        density[py, px] += 1

# Log-scale the density so rare points are still visible
log_density = np.log1p(density.astype(np.float64))
normalized = (log_density / log_density.max() * 255).astype(np.uint8)

Image.fromarray(normalized, mode='L').save('simple_attractor.png')
