"""
simple_sierpinski.py — render a Sierpinski triangle via the chaos game:
start at a random point, then repeatedly jump halfway to a randomly chosen
vertex of an equilateral triangle. After many iterations, the visited
points trace out the Sierpinski gasket.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image


SIZE = 600
N_POINTS = 200_000

# Three vertices of an equilateral triangle, centred on the canvas.
vertices = np.array([
    [SIZE * 0.5, SIZE * 0.10],   # top
    [SIZE * 0.10, SIZE * 0.85],  # bottom-left
    [SIZE * 0.90, SIZE * 0.85],  # bottom-right
])

# Reproducible random sequence so the dot pattern is consistent.
rng = np.random.default_rng(0)
indices = rng.integers(0, 3, size=N_POINTS)

# Iteratively jump halfway from the current point to the chosen vertex.
# This is the Iterated Function System (IFS) form of the Sierpinski gasket.
point = np.array([SIZE * 0.5, SIZE * 0.5])  # arbitrary start
visited = np.zeros((N_POINTS, 2), dtype=np.int32)
for i, vi in enumerate(indices):
    point = (point + vertices[vi]) / 2.0
    visited[i] = point.round().astype(np.int32)

canvas = np.zeros((SIZE, SIZE), dtype=np.uint8)
xs = visited[:, 0]
ys = visited[:, 1]
inside = (xs >= 0) & (xs < SIZE) & (ys >= 0) & (ys < SIZE)
# Drop the first 20 points — they are transients before the orbit settles on
# the attractor and would otherwise leave a few stray pixels.
canvas[ys[inside][20:], xs[inside][20:]] = 255

Image.fromarray(canvas, mode='L').save('simple_sierpinski.png')
print(f"Saved simple_sierpinski.png — {N_POINTS} chaos-game points on {SIZE}x{SIZE}")
