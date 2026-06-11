"""
turing_starter.py - Exercise 3 scaffold for Gray-Scott.

The main loop and rendering are wired up. You implement the per-step
Gray-Scott update inside `step()`.

Pixels2GenAI Project
"""

import numpy as np
import matplotlib
from PIL import Image
import imageio.v2 as imageio

GRID = 160
SCALE = 2
NUM_FRAMES = 50
STEPS_PER_FRAME = 30
FPS = 16
DU = 0.16
DV = 0.08
FEED = 0.040
KILL = 0.060
DT = 1.0


def laplacian(field):
    return (np.roll(field, +1, axis=0) + np.roll(field, -1, axis=0)
            + np.roll(field, +1, axis=1) + np.roll(field, -1, axis=1)
            - 4 * field)


def step(U, V):
    """TODO: implement the Gray-Scott update equations.

    Lu = laplacian(U); Lv = laplacian(V)
    uvv = U * V * V
    U_new = U + DT * (DU * Lu - uvv + FEED * (1 - U))
    V_new = V + DT * (DV * Lv + uvv - (FEED + KILL) * V)
    Clip both to [0, 1] before returning.
    """
    return U, V


def render(V):
    cmap = matplotlib.colormaps['inferno']
    img = (cmap(np.clip(V, 0, 1))[..., :3] * 255).astype(np.uint8)
    return np.repeat(np.repeat(img, SCALE, axis=0), SCALE, axis=1)


def main():
    rng = np.random.default_rng(0)
    U = np.ones((GRID, GRID))
    V = np.zeros((GRID, GRID))
    for _ in range(6):
        r, c = rng.integers(20, GRID - 30), rng.integers(20, GRID - 30)
        V[r:r + 8, c:c + 8] = 0.5 + 0.5 * rng.random((8, 8))
        U[r:r + 8, c:c + 8] = 0.5 * rng.random((8, 8))
    frames = []
    for _ in range(NUM_FRAMES):
        for _ in range(STEPS_PER_FRAME):
            U, V = step(U, V)
        frames.append(render(V))
    imageio.mimsave('turing_starter.gif', frames, fps=FPS)


if __name__ == '__main__':
    main()
