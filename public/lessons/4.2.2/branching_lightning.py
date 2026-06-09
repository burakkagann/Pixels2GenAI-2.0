"""
branching_lightning.py — main bolt plus a probabilistic side branch at each
subdivision step. Same midpoint-displacement core as simple_lightning.py,
but at each subdivision a coin flip decides whether to spawn a smaller bolt
heading off at an angle from the new vertex. The side bolts recurse with a
shorter length budget and dimmer colour, which is the cheapest way to get
the multi-branch fork look without simulating the underlying physics.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image, ImageDraw


SIZE = (600, 800)
SEED = 11


def midpoint_bolt(start, end, displacement, depth, rng):
    """Same midpoint-displacement subdivision used in simple_lightning.py."""
    if depth == 0:
        return [start, end]
    mid = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = (dx * dx + dy * dy) ** 0.5 or 1.0
    nx, ny = -dy / length, dx / length
    offset = rng.uniform(-displacement, displacement)
    mid_p = (mid[0] + nx * offset, mid[1] + ny * offset)
    left  = midpoint_bolt(start, mid_p, displacement / 2, depth - 1, rng)
    right = midpoint_bolt(mid_p, end,   displacement / 2, depth - 1, rng)
    return left + right[1:]


def draw_bolt(draw, start, end, displacement, depth, rng,
              brightness=255, branch_prob=0.3):
    """Draw one polyline bolt, then probabilistically spawn child bolts."""
    points = midpoint_bolt(start, end, displacement, depth, rng)
    color = (int(0.7 * brightness), int(0.86 * brightness), brightness)
    draw.line(points, fill=color, width=2 if brightness > 150 else 1)

    if brightness < 80:
        return
    # Spawn child bolts at random interior vertices.
    for i in range(2, len(points) - 1, 4):
        if rng.random() < branch_prob:
            anchor = points[i]
            # Aim the child at an angled offset from the parent direction
            dx, dy = end[0] - start[0], end[1] - start[1]
            angle = np.arctan2(dy, dx) + rng.uniform(-1.0, 1.0)
            length = rng.uniform(80, 180)
            child_end = (anchor[0] + length * np.cos(angle),
                         anchor[1] + length * np.sin(angle))
            draw_bolt(draw, anchor, child_end, displacement * 0.6,
                      max(2, depth - 2), rng,
                      brightness=int(brightness * 0.6),
                      branch_prob=branch_prob * 0.6)


rng = np.random.default_rng(SEED)
img = Image.new('RGB', SIZE, color=(6, 8, 22))
draw_bolt(ImageDraw.Draw(img),
          start=(SIZE[0] / 2, 30),
          end=(SIZE[0] / 2, SIZE[1] - 30),
          displacement=120, depth=8, rng=rng)

img.save('branching_lightning.png')
print('Saved branching_lightning.png')
