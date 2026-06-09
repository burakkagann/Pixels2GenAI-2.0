"""
simple_lightning.py — generate a single lightning bolt via midpoint
displacement on a polyline. Start with a straight segment, then recursively
subdivide each edge by inserting a new vertex at the midpoint perturbed
perpendicularly by a random amount. The perturbation scale halves at every
subdivision, which is what gives the bolt its characteristic fractal jaggedness.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image, ImageDraw


SIZE = (600, 800)  # (width, height)
SEED = 7


def subdivide_polyline(points, displacement, decay=0.5, depth=7, rng=None):
    """Recursively subdivide a polyline using midpoint displacement.

    Each edge is split in half; the midpoint is offset perpendicular to the
    edge by a random amount uniform in [-displacement, +displacement]. The
    displacement scale shrinks by `decay` at every recursion level so the
    perturbations have a 1/f-like spectrum — the characteristic look of
    natural fractals.
    """
    rng = rng if rng is not None else np.random.default_rng()
    if depth == 0:
        return points
    new = [points[0]]
    for i in range(len(points) - 1):
        a, b = points[i], points[i + 1]
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        # Unit perpendicular to (b - a)
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = (dx * dx + dy * dy) ** 0.5 or 1.0
        nx, ny = -dy / length, dx / length
        offset = rng.uniform(-displacement, displacement)
        mid_perturbed = (mid[0] + nx * offset, mid[1] + ny * offset)
        new.append(mid_perturbed)
        new.append(b)
    return subdivide_polyline(new, displacement * decay, decay, depth - 1, rng)


rng = np.random.default_rng(SEED)
# Vertical bolt from top to bottom
start = (SIZE[0] / 2, 30)
end   = (SIZE[0] / 2, SIZE[1] - 30)
points = subdivide_polyline([start, end], displacement=120, decay=0.5,
                            depth=8, rng=rng)

img = Image.new('RGB', SIZE, color=(8, 10, 25))
draw = ImageDraw.Draw(img)
draw.line(points, fill=(180, 220, 255), width=2)
img.save('simple_lightning.png')
print(f"Saved simple_lightning.png — {len(points)} vertices")
