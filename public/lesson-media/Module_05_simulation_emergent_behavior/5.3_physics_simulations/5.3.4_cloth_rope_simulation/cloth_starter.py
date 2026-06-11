"""
cloth_starter.py - Exercise 3 scaffold for Verlet-cloth.

The render loop and gravity-Verlet integrate step are wired up. You
implement `relax()` - the distance-constraint enforcement.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as imageio

WIDTH, HEIGHT = 520, 520
COLS, ROWS = 16, 12
SPACING = 24
CLOTH_OFFSET = (100, 60)
GRAVITY = np.array([0.0, 0.45])
DAMPING = 0.985
RELAX_ITERS = 14
NUM_FRAMES = 180
FPS = 30


def integrate(positions, previous):
    new = positions + (positions - previous) * DAMPING + GRAVITY
    return new, positions


def relax(positions):
    """TODO: enforce that every spring is exactly SPACING long.

    For each horizontal and vertical neighbour pair:
      - delta = p2 - p1
      - distance = |delta|
      - correction = (distance - SPACING) / distance * delta * 0.5
      - move p1 by +correction, p2 by -correction

    Run the whole pass RELAX_ITERS times for convergence. After each iter,
    re-pin the top two corners to their starting positions.
    """
    return positions


def render(positions):
    img = Image.new('RGB', (WIDTH, HEIGHT), (10, 12, 20))
    draw = ImageDraw.Draw(img)
    for r in range(ROWS):
        for c in range(COLS):
            if c < COLS - 1:
                draw.line([tuple(positions[r, c]),
                           tuple(positions[r, c + 1])],
                          fill=(110, 200, 250), width=1)
            if r < ROWS - 1:
                draw.line([tuple(positions[r, c]),
                           tuple(positions[r + 1, c])],
                          fill=(110, 200, 250), width=1)
    return np.array(img)


def main():
    positions = np.zeros((ROWS, COLS, 2))
    for r in range(ROWS):
        for c in range(COLS):
            positions[r, c] = (CLOTH_OFFSET[0] + c * SPACING,
                               CLOTH_OFFSET[1] + r * SPACING)
    previous = positions.copy()
    frames = []
    for _ in range(NUM_FRAMES):
        positions, previous = integrate(positions, previous)
        positions = relax(positions)
        frames.append(render(positions))
    imageio.mimsave('cloth_starter.gif', frames, fps=FPS)


if __name__ == '__main__':
    main()
