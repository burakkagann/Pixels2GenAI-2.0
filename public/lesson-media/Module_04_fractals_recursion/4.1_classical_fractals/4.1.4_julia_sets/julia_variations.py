"""
julia_variations.py — render a 2x3 grid of Julia sets for different values of c.
Each c produces a qualitatively different shape: dendrites, swirls, "dust", and
San Marco lagoon-like silhouettes. The grid shows how a single parameter on the
quadratic map z -> z^2 + c sweeps an entire family of connected fractals.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image


TILE = 400
MAX_ITER = 200
ROWS, COLS = 2, 3

# Six well-known Julia-set parameters, in iteration order.
C_VALUES = [
    complex(-0.7, 0.27015),    # the dendrite c used by simple_julia.py
    complex(-0.8, 0.156),      # connected, "branchy"
    complex(0.285, 0.01),      # San Marco-like
    complex(-0.4, 0.6),        # rabbit
    complex(-0.835, -0.2321),  # spirals
    complex(0.45, 0.1428),     # dust-like, disconnected
]

LABELS = ['-0.7+0.27j', '-0.8+0.16j', '0.29+0.01j',
          '-0.4+0.6j', '-0.84-0.23j', '0.45+0.14j']


def julia(c, size=TILE, max_iter=MAX_ITER):
    """Render one Julia set tile as a uint8 grayscale array."""
    x = np.linspace(-1.6, 1.6, size)
    y = np.linspace(-1.6, 1.6, size)
    real, imag = np.meshgrid(x, y)
    z = real + 1j * imag

    iters = np.zeros(z.shape, dtype=np.int32)
    for _ in range(max_iter):
        bounded = np.abs(z) <= 2
        z[bounded] = z[bounded] ** 2 + c
        iters[bounded] += 1

    out = np.zeros((size, size), dtype=np.uint8)
    outside = iters < max_iter
    out[outside] = (iters[outside] / max_iter * 255).astype(np.uint8)
    return out


# Assemble the grid.
grid = np.zeros((ROWS * TILE, COLS * TILE), dtype=np.uint8)
for i, c in enumerate(C_VALUES):
    row, col = i // COLS, i % COLS
    print(f'Tile {i + 1}/6: c = {c}')
    grid[row * TILE:(row + 1) * TILE, col * TILE:(col + 1) * TILE] = julia(c)

Image.fromarray(grid, mode='L').save('julia_variations.png')
print(f"Saved julia_variations.png — labels (row-major): {LABELS}")
