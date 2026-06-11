"""
nbody_starter.py - Exercise 3 scaffold for N-body gravity.

The simulation loop and rendering are wired up. You implement
`accelerations()` - the vectorised pairwise gravity computation.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as imageio

WIDTH, HEIGHT = 540, 540
NUM_FRAMES = 200
FPS = 30
G = 1.6
SOFTENING = 6.0
DT = 0.45
BG = (4, 6, 18)
TRAIL_FADE = 0.92


def accelerations(positions, masses):
    """TODO: compute the acceleration of every body due to gravity from
    every other body.

    Newton's law: a_i = G * sum_{j != i} m_j * (r_j - r_i) / |r_j - r_i|^3.

    Use SOFTENING^2 added to |r|^2 to avoid blow-ups at close range. Use
    np.fill_diagonal to zero out the self-attraction term.
    """
    return np.zeros_like(positions)


def render(canvas, positions, masses):
    canvas = (canvas.astype(np.float32) * TRAIL_FADE).astype(np.uint8)
    canvas[:, :] = np.maximum(canvas, np.array(BG, dtype=np.uint8))
    img = Image.fromarray(canvas)
    draw = ImageDraw.Draw(img)
    for (x, y), m in zip(positions, masses):
        r = max(2.0, np.sqrt(m) * 0.9)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(220, 220, 255))
    return np.array(img)


def main():
    centre = np.array([WIDTH / 2, HEIGHT / 2])
    positions = np.array([
        centre,
        centre + [120, 0],
        centre + [0, 160],
        centre + [-100, -50],
    ], dtype=float)
    velocities = np.array([
        [0, 0],
        [0, 1.7],
        [-1.5, 0],
        [1.2, -0.9],
    ], dtype=float)
    masses = np.array([220.0, 5.0, 4.0, 3.0])

    canvas = np.full((HEIGHT, WIDTH, 3), BG, dtype=np.uint8)
    a = accelerations(positions, masses)

    frames = []
    for _ in range(NUM_FRAMES):
        velocities += 0.5 * a * DT
        positions += velocities * DT
        a = accelerations(positions, masses)
        velocities += 0.5 * a * DT
        canvas = render(canvas, positions, masses)
        frames.append(canvas.copy())
    imageio.mimsave('nbody_starter.gif', frames, fps=FPS)


if __name__ == '__main__':
    main()
