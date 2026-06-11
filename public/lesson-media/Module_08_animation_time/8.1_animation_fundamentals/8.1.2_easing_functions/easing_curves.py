"""
easing_curves.py — render a 3x3 grid plot of the nine most-used easing
functions: linear, ease-in/out quadratic, ease-in/out cubic, ease-in/out
quartic, sine, and a bounce. Each curve maps t in [0, 1] to an eased
position in [0, 1]. Drives every animated parameter in this module.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image, ImageDraw


SIZE = 720
ROWS, COLS = 3, 3
TILE = SIZE // ROWS
PADDING = 20


def linear(t):           return t
def ease_in_quad(t):     return t * t
def ease_out_quad(t):    return 1 - (1 - t) ** 2
def ease_in_out_quad(t): return np.where(t < 0.5, 2 * t * t, 1 - (-2 * t + 2) ** 2 / 2)
def ease_in_cubic(t):    return t ** 3
def ease_out_cubic(t):   return 1 - (1 - t) ** 3
def ease_in_out_cubic(t):
    return np.where(t < 0.5, 4 * t ** 3, 1 - (-2 * t + 2) ** 3 / 2)
def ease_sine(t):        return -(np.cos(np.pi * t) - 1) / 2


def bounce(t):
    """Robert Penner's ease-out bounce."""
    n1 = 7.5625
    d1 = 2.75
    out = np.empty_like(t)
    mask1 = t < 1 / d1
    mask2 = np.logical_and(~mask1, t < 2 / d1)
    mask3 = np.logical_and(~(mask1 | mask2), t < 2.5 / d1)
    mask4 = ~(mask1 | mask2 | mask3)
    out[mask1] = n1 * t[mask1] ** 2
    t2 = t[mask2] - 1.5 / d1
    out[mask2] = n1 * t2 * t2 + 0.75
    t3 = t[mask3] - 2.25 / d1
    out[mask3] = n1 * t3 * t3 + 0.9375
    t4 = t[mask4] - 2.625 / d1
    out[mask4] = n1 * t4 * t4 + 0.984375
    return out


CURVES = [
    ('linear', linear),
    ('ease-in quad', ease_in_quad),
    ('ease-out quad', ease_out_quad),
    ('ease-in-out quad', ease_in_out_quad),
    ('ease-in cubic', ease_in_cubic),
    ('ease-out cubic', ease_out_cubic),
    ('ease-in-out cubic', ease_in_out_cubic),
    ('ease sinusoidal', ease_sine),
    ('ease-out bounce', bounce),
]


canvas = Image.new('RGB', (SIZE, SIZE), (18, 20, 30))
draw = ImageDraw.Draw(canvas)

t = np.linspace(0, 1, 256)
plot_size = TILE - 2 * PADDING

for idx, (name, fn) in enumerate(CURVES):
    r, c = idx // COLS, idx % COLS
    ox = c * TILE + PADDING
    oy = r * TILE + PADDING

    # Plot frame
    draw.rectangle([ox, oy, ox + plot_size, oy + plot_size], outline=(60, 65, 85))

    # Diagonal reference (linear)
    draw.line(
        [(ox, oy + plot_size), (ox + plot_size, oy)],
        fill=(50, 55, 70), width=1,
    )

    # Plot the eased curve
    values = fn(t.copy())
    pts = []
    for ti, vi in zip(t, values):
        px = int(ox + ti * plot_size)
        py = int(oy + (1 - vi) * plot_size)
        pts.append((px, py))
    draw.line(pts, fill=(120, 200, 255), width=2)

    # Label
    draw.text((ox + 4, oy + 4), name, fill=(200, 210, 230))

canvas.save('easing_curves.png')
print(f"Saved easing_curves.png — {len(CURVES)} easing functions in a {ROWS}x{COLS} grid")
