"""
fluid_starter.py - Exercise 3 scaffold for the grid-based fluid solver.

The simulation loop, advection, and projection are wired up. You implement
`diffuse()` - the Gauss-Seidel relaxation step.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image
import imageio.v2 as imageio

GRID = 80
SCALE = 5
NUM_FRAMES = 100
FPS = 24
DT = 0.18
VISCOSITY = 1.0e-4
DIFFUSION = 1.0e-4
SOLVER_ITERS = 12
INJECT_STRENGTH = 60.0
SWIRL_STRENGTH = 100.0


def diffuse(field, diff, dt):
    """TODO: implement Gauss-Seidel relaxation for the diffusion equation.

    The discrete diffusion equation says:

        field[i,j] = (old[i,j] + a*sum_of_4_neighbours) / (1 + 4*a)

    where a = dt * diff * GRID * GRID. Run this update SOLVER_ITERS times,
    each iteration using the most-recently-updated `field` (in-place).
    """
    return field  # replace me


def advect(field, vx, vy, dt):
    out = np.zeros_like(field)
    dt0 = dt * GRID
    xs, ys = np.meshgrid(np.arange(GRID), np.arange(GRID), indexing='xy')
    px = np.clip(xs - dt0 * vx, 0.5, GRID - 1.5)
    py = np.clip(ys - dt0 * vy, 0.5, GRID - 1.5)
    i0, j0 = px.astype(int), py.astype(int)
    i1, j1 = i0 + 1, j0 + 1
    s1, s0 = px - i0, 1 - (px - i0)
    t1, t0 = py - j0, 1 - (py - j0)
    out[ys, xs] = (
        s0 * (t0 * field[j0, i0] + t1 * field[j1, i0])
        + s1 * (t0 * field[j0, i1] + t1 * field[j1, i1])
    )
    return out


def project(vx, vy):
    div = np.zeros_like(vx)
    p = np.zeros_like(vx)
    div[1:-1, 1:-1] = -0.5 * (
        vx[1:-1, 2:] - vx[1:-1, :-2] + vy[2:, 1:-1] - vy[:-2, 1:-1]
    ) / GRID
    for _ in range(SOLVER_ITERS):
        p[1:-1, 1:-1] = (
            div[1:-1, 1:-1]
            + p[2:, 1:-1] + p[:-2, 1:-1] + p[1:-1, 2:] + p[1:-1, :-2]
        ) / 4
    vx[1:-1, 1:-1] -= 0.5 * GRID * (p[1:-1, 2:] - p[1:-1, :-2])
    vy[1:-1, 1:-1] -= 0.5 * GRID * (p[2:, 1:-1] - p[:-2, 1:-1])
    return vx, vy


def render(density):
    norm = np.clip(density / max(density.max(), 1e-3), 0, 1)
    img = np.stack([0.3 + 0.7 * norm, 0.1 + 0.3 * norm**0.8,
                    0.45 + 0.55 * (1 - norm)**1.5], axis=-1)
    img = (img * 255).clip(0, 255).astype(np.uint8)
    return np.repeat(np.repeat(img, SCALE, axis=0), SCALE, axis=1)


def main():
    vx = np.zeros((GRID, GRID))
    vy = np.zeros((GRID, GRID))
    density = np.zeros((GRID, GRID))
    cx, cy = GRID // 4, GRID // 2

    frames = []
    for _ in range(NUM_FRAMES):
        density[cy - 2:cy + 3, cx - 2:cx + 3] += INJECT_STRENGTH * DT
        vx[cy - 2:cy + 3, cx - 2:cx + 3] += SWIRL_STRENGTH * DT
        vx = diffuse(vx, VISCOSITY, DT)
        vy = diffuse(vy, VISCOSITY, DT)
        vx, vy = project(vx, vy)
        vx = advect(vx, vx, vy, DT)
        vy = advect(vy, vx, vy, DT)
        vx, vy = project(vx, vy)
        density = diffuse(density, DIFFUSION, DT)
        density = advect(density, vx, vy, DT)
        density *= 0.995
        frames.append(render(density))
    imageio.mimsave('fluid_starter.gif', frames, fps=FPS)


if __name__ == '__main__':
    main()
