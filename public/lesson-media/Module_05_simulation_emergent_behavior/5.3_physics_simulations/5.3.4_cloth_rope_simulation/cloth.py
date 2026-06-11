"""
cloth.py - A cloth/rope simulation using Verlet integration with
distance-constraint relaxation. The cloth is a grid of point masses
connected by springs. Each frame: integrate, then iteratively enforce
the spring lengths.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as imageio

# ---------- CONFIG ----------
WIDTH, HEIGHT = 520, 520
COLS, ROWS = 18, 14
SPACING = 22
CLOTH_OFFSET = (90, 60)

GRAVITY = np.array([0.0, 0.45])
WIND = 0.15
DAMPING = 0.985
RELAX_ITERS = 18
NUM_FRAMES = 220
FPS = 30

BG = (10, 12, 20)
GRID_COLOUR = (110, 200, 250)
PIN_COLOUR = (255, 150, 100)
# ----------------------------


def initial_positions():
    positions = np.zeros((ROWS, COLS, 2))
    for r in range(ROWS):
        for c in range(COLS):
            positions[r, c] = (CLOTH_OFFSET[0] + c * SPACING,
                               CLOTH_OFFSET[1] + r * SPACING)
    return positions


def integrate(positions, previous):
    """Verlet step: x_{n+1} = x_n + (x_n - x_{n-1}) * damping + accel * dt^2."""
    wind = np.random.normal(0, WIND, positions.shape)
    accel = GRAVITY + wind
    new = positions + (positions - previous) * DAMPING + accel
    return new, positions


def relax(positions):
    """Iteratively enforce that each spring is exactly SPACING long."""
    pins = [(0, 0), (0, COLS - 1)]    # top two corners pinned
    for _ in range(RELAX_ITERS):
        # horizontal links
        for r in range(ROWS):
            for c in range(COLS - 1):
                p1 = positions[r, c]
                p2 = positions[r, c + 1]
                delta = p2 - p1
                d = np.linalg.norm(delta) + 1e-6
                correction = (d - SPACING) / d * delta * 0.5
                positions[r, c] += correction
                positions[r, c + 1] -= correction
        # vertical links
        for r in range(ROWS - 1):
            for c in range(COLS):
                p1 = positions[r, c]
                p2 = positions[r + 1, c]
                delta = p2 - p1
                d = np.linalg.norm(delta) + 1e-6
                correction = (d - SPACING) / d * delta * 0.5
                positions[r, c] += correction
                positions[r + 1, c] -= correction
        # re-pin
        for (r, c) in pins:
            positions[r, c] = (CLOTH_OFFSET[0] + c * SPACING,
                               CLOTH_OFFSET[1] + r * SPACING)
    return positions


def render(positions, frame_idx):
    img = Image.new('RGB', (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    for r in range(ROWS):
        for c in range(COLS):
            if c < COLS - 1:
                draw.line([tuple(positions[r, c]),
                           tuple(positions[r, c + 1])],
                          fill=GRID_COLOUR, width=1)
            if r < ROWS - 1:
                draw.line([tuple(positions[r, c]),
                           tuple(positions[r + 1, c])],
                          fill=GRID_COLOUR, width=1)
    for (r, c) in [(0, 0), (0, COLS - 1)]:
        x, y = positions[r, c]
        draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=PIN_COLOUR)
    return np.array(img)


def main():
    np.random.seed(0)
    positions = initial_positions()
    previous = positions.copy()
    frames = []
    for frame in range(NUM_FRAMES):
        positions, previous = integrate(positions, previous)
        positions = relax(positions)
        frames.append(render(positions, frame))
        if frame == NUM_FRAMES // 2:
            Image.fromarray(frames[-1]).save('cloth_frame.png')
    imageio.mimsave('cloth.gif', frames, fps=FPS)
    Image.fromarray(frames[-1]).save('cloth_final.png')
    print(f'Wrote cloth.gif ({NUM_FRAMES} frames)')


if __name__ == '__main__':
    main()
