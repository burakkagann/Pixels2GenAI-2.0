"""
attractor_variations.py — four de Jong attractors with different (a, b, c, d)
quadruples, rendered as a 2x2 grid. Tiny changes in the parameters produce
visually distinct attractors — the signature of strange attractors.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image


PANEL = 300
CANVAS_W, CANVAS_H = PANEL * 2, PANEL * 2
NUM_POINTS = 200_000

quadruples = [
    (1.641, 1.902, 0.316, 1.525),
    (1.4,  -2.3,   2.4,  -2.1),
    (-2.0,  -2.0, -1.2,   2.0),
    (1.5,  -1.8,   1.6,   0.9),
]


def render_panel(canvas, x_off, y_off, params):
    a, b, c, d = params
    x, y = 0.1, 0.1
    # Burn-in
    for _ in range(100):
        x = np.sin(a * y) - np.cos(b * x)
        y_new = np.sin(c * x) - np.cos(d * y)
        y = y_new

    density = np.zeros((PANEL, PANEL), dtype=np.uint32)

    def to_pixel(v):
        return int((v + 2) / 4 * (PANEL - 1))

    for _ in range(NUM_POINTS):
        x_new = np.sin(a * y) - np.cos(b * x)
        y_new = np.sin(c * x) - np.cos(d * y)
        x, y = x_new, y_new
        px, py = to_pixel(x), to_pixel(y)
        if 0 <= px < PANEL and 0 <= py < PANEL:
            density[py, px] += 1

    log_density = np.log1p(density.astype(np.float64))
    if log_density.max() > 0:
        norm = (log_density / log_density.max() * 255).astype(np.uint8)
    else:
        norm = np.zeros_like(density, dtype=np.uint8)
    canvas[y_off:y_off + PANEL, x_off:x_off + PANEL] = norm


canvas = np.zeros((CANVAS_H, CANVAS_W), dtype=np.uint8)
for idx, q in enumerate(quadruples):
    col = idx % 2
    row = idx // 2
    render_panel(canvas, col * PANEL, row * PANEL, q)

Image.fromarray(canvas, mode='L').save('attractor_variations.png')
