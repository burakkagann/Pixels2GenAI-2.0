"""
turing_patterns.py - Gray-Scott reaction-diffusion system. Two chemicals
(U and V) diffuse at different rates while reacting with one another.
The classic Turing observation: this produces stable spatial patterns -
spots, stripes, and labyrinths - from random initial noise.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image
import imageio.v2 as imageio

# ---------- CONFIG ----------
GRID = 160
SCALE = 2
NUM_FRAMES = 56
STEPS_PER_FRAME = 40
FPS = 16

DU = 0.16      # diffusion rate of U
DV = 0.08      # diffusion rate of V
FEED = 0.040   # feed rate (Gray-Scott parameter F)
KILL = 0.060   # kill rate (Gray-Scott parameter k)
DT = 1.0

BG = (8, 6, 14)
# ----------------------------


def laplacian(field):
    """5-point stencil Laplacian with periodic boundaries (np.roll)."""
    return (
        np.roll(field, +1, axis=0)
        + np.roll(field, -1, axis=0)
        + np.roll(field, +1, axis=1)
        + np.roll(field, -1, axis=1)
        - 4 * field
    )


def initial_state():
    U = np.ones((GRID, GRID))
    V = np.zeros((GRID, GRID))
    # seed a few small noisy regions
    rng = np.random.default_rng(0)
    for _ in range(8):
        r = rng.integers(20, GRID - 30)
        c = rng.integers(20, GRID - 30)
        s = rng.integers(4, 10)
        V[r - s:r + s, c - s:c + s] = 0.5 + 0.5 * rng.random((2 * s, 2 * s))
        U[r - s:r + s, c - s:c + s] = 0.5 * rng.random((2 * s, 2 * s))
    return U, V


def step(U, V):
    Lu = laplacian(U)
    Lv = laplacian(V)
    uvv = U * V * V
    U = U + DT * (DU * Lu - uvv + FEED * (1 - U))
    V = V + DT * (DV * Lv + uvv - (FEED + KILL) * V)
    np.clip(U, 0, 1, out=U)
    np.clip(V, 0, 1, out=V)
    return U, V


def render(U, V):
    import matplotlib as mpl
    cmap = mpl.colormaps['inferno']
    norm = np.clip(V, 0, 1)
    img = (cmap(norm)[..., :3] * 255).astype(np.uint8)
    return np.repeat(np.repeat(img, SCALE, axis=0), SCALE, axis=1)


def main():
    U, V = initial_state()
    frames = []
    for frame in range(NUM_FRAMES):
        for _ in range(STEPS_PER_FRAME):
            U, V = step(U, V)
        img = render(U, V)
        frames.append(img)
        if frame == NUM_FRAMES // 2:
            Image.fromarray(img).save('turing_frame.png')

    imageio.mimsave('turing_patterns.gif', frames, fps=FPS)
    Image.fromarray(frames[-1]).save('turing_final.png')
    print(f'Wrote turing_patterns.gif ({NUM_FRAMES} frames)')


if __name__ == '__main__':
    main()
